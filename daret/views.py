from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from authentication.utils import APIAccessMixin
from django.shortcuts import get_object_or_404
import json
from django.db.models import Q
from tour.models import Tour
from notifications.utils import create_notification
from .utils import generate_code_group
from .models import Daret, JoinDaret
from .serializers import DaretSerializer, JoinDaretSerializer


class ManageDaretView(APIAccessMixin, APIView):
    """Manage Darets"""
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id_daret=None, *args, **kwargs):
        """Retrieve Darets filtered by the owner or as a participant."""
        user = request.user

        if id_daret:
            # Retrieve a specific Daret by its codeGroup
            daret = get_object_or_404(Daret, pk=id_daret)

            # Check if the user is either the owner or a participant
            if daret.owner == user or JoinDaret.objects.filter(daret=daret, participant=user, is_confirmed=True).exists():
                serializer = DaretSerializer(daret)
                return Response({'success': True, 'data': serializer.data}, status=200)
            else:
                return Response({'success': False, 'message': 'You do not have access to this Daret.'}, status=403)
        else:
            # Retrieve all Darets where the user is the owner or a participant
            darets = Daret.objects.filter(Q(owner=user) | Q(
                joinDarets__participant=user, joinDarets__is_confirmed=True)).distinct()
            serializer = DaretSerializer(darets, many=True)

            return Response({'success': True, 'data': serializer.data}, status=200)

    def post(self, request, id_daret=None, *args, **kwargs):
        """Join existing Daret or create a new one"""
        user = request.user

        if id_daret:
            # Look for an existing Daret by codeGroup
            daret = get_object_or_404(Daret, codeGroup=id_daret)

            # Check if the user is already a participant
            existing_participant = JoinDaret.objects.filter(
                participant=user, daret=daret).first()
            if existing_participant:
                if existing_participant.is_confirmed:
                    return Response({'success': False, 'message': 'You are already a participant in this Daret'}, status=400)
                else:
                    return Response({'success': False, 'message': 'Your request is pending confirmation from the owner.'}, status=400)

            # Create participant data with IDs and set is_confirmed to False
            participant_data = {
                "participant": user.id,
                "daret": daret.id,
                "is_confirmed": False,  # Request is pending
            }

            # Serialize and save the participant request
            serializer = JoinDaretSerializer(data=participant_data)
            if serializer.is_valid():
                serializer.save()

                # Create a notification for the Daret owner
                create_notification(
                    user_source=user,  # The participant who is sending the request
                    user_destination=daret.owner,  # The owner of the Daret
                    message=(
                        "{} has requested to join your Daret {}."
                        .format(user.username, daret.name)
                    )

                )

                return Response({'success': True, 'message': 'Your request to join the Daret has been sent. Awaiting owner confirmation.'}, status=200)
            return Response({'success': False, 'message': serializer.errors}, status=400)

        else:
            # Case 2: User is creating a new Daret
            # Parse JSON body
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return Response({'success': False, 'message': 'Invalid JSON data'}, status=400)

            # Convert 'is_part' from string to boolean if necessary
            if isinstance(data.get('is_part'), str):
                is_part_str = data.get('is_part').lower().strip()
                if is_part_str == 'true':
                    data['is_part'] = True
                elif is_part_str == 'false':
                    data['is_part'] = False
                else:
                    return Response({'success': False, 'message': 'Invalid value for is_part'}, status=400)

            # Extract necessary fields
            owner = user
            name = data.get('name')
            date_start = data.get('date_start')
            mensuel = data.get('mensuel')
            is_part = data.get('is_part')

            # Check if a Daret with the same owner, name, date_start, mensuel, and is_part already exists
            if Daret.objects.filter(owner=owner, name=name, date_start=date_start, mensuel=mensuel, is_part=is_part).exists():
                return Response({'success': False, 'message': 'Daret with the same information already exists'}, status=400)

            # Automatically generate a new codeGroup
            data['codeGroup'] = generate_code_group()

            # Set nbre_elements if is_part is True
            if is_part:
                data['nbre_elements'] = 1

            # Serialize and save the new Daret
            serializer = DaretSerializer(data=data)
            if serializer.is_valid():

                daret_instance = serializer.save(owner=owner)

                # Create the JoinDaret record for the owner if he is part of the group
                if is_part:

                    JoinDaret.objects.create(
                        participant=user,
                        daret=daret_instance,
                        is_confirmed=True,
                    )

                    Tour.objects.create(
                        user=user,
                        daret=daret_instance,
                        date_obtenu=datetime.now(),
                        ordre=1,
                    )

                return Response({'success': True, 'message': 'Daret created successfully'}, status=201)
            return Response({'success': False, 'message': serializer.errors}, status=400)

    def put(self, request, id_daret, *args, **kwargs):
        """Update an existing Daret"""
        # Check if the user is the owner of the Daret
        daret = get_object_or_404(Daret, pk=id_daret)

        if daret.owner != request.user:
            return Response({'success': False, 'message': 'You are not authorized to update this Daret.'}, status=403)

        # Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({'success': False, 'message': 'Invalid JSON data'}, status=400)

        # Validate required fields if necessary
        required_fields = ['name', 'date_start', 'mensuel']
        for field in required_fields:
            if field in data and not data[field]:
                return Response({'success': False, 'message': f'{field} cannot be empty.'}, status=400)

        # Handle is_part conversion from string to boolean
        if isinstance(data.get('is_part'), str):
            is_part_str = data.get('is_part').lower().strip()
            if is_part_str == 'true':
                data['is_part'] = True
            elif is_part_str == 'false':
                data['is_part'] = False
            else:
                return Response({'success': False, 'message': 'Invalid value for is_part'}, status=400)

        is_part = data.get('is_part')

        # Use partial updates
        serializer = DaretSerializer(daret, data=data, partial=True)
        if serializer.is_valid():
            updated_daret = serializer.save()

            # If the current user changes is_part to true, add to joinDaret and tour
            if is_part:
                daret.nbre_elements += 1
                daret.save()

                # Check if the user is already a participant in JoinDaret
                existing_join_daret = JoinDaret.objects.filter(
                    participant=request.user, daret=updated_daret).first()

                if not existing_join_daret:
                    JoinDaret.objects.create(
                        participant=request.user,
                        daret=updated_daret,
                        is_confirmed=True,
                    )

                # Check if the user is already part of the Tour
                existing_tour_daret = Tour.objects.filter(
                    # Use daret for Daret reference
                    user=request.user, daret=updated_daret).first()

                if not existing_tour_daret:
                    Tour.objects.create(
                        user=request.user,
                        daret=updated_daret,  # Correct the field name
                        date_obtenu=datetime.now(),
                        ordre=1,
                    )
            else:
                # If the current user changes is_part to false, remove from JoinDaret and Tour
                daret.nbre_elements -= 1
                daret.save()

                # Remove user from the Tour
                # Correct the field name
                Tour.objects.filter(user=request.user,
                                    daret=updated_daret).delete()

                # Remove user from JoinDaret
                JoinDaret.objects.filter(
                    participant=request.user, daret=updated_daret).delete()

            # Notify all participants about the Daret update except the owner
            participants = JoinDaret.objects.filter(
                daret=daret).exclude(participant=request.user)
            for participant in participants:
                create_notification(
                    user_source=request.user,
                    user_destination=participant.participant,
                    message=(
                        "The Daret {} has been updated by {}."
                        .format(daret.name, request.user.username)
                    )

                )

            return Response({'success': True, 'message': 'Daret updated successfully', 'data': DaretSerializer(updated_daret).data}, status=200)

        return Response({'success': False, 'message': serializer.errors}, status=400)

    def delete(self, request, id_daret, *args, **kwargs):
        """Delete a Daret"""
        # Retrieve the Daret or return 404 if not found
        daret = get_object_or_404(Daret, pk=id_daret)

        # Check if the user is the owner of the Daret
        if daret.owner != request.user:
            return Response({'success': False, 'message': 'You are not authorized to delete this Daret.'}, status=403)

        # Delete the Daret
        daret.delete()
        return Response({'success': True, 'message': 'Daret deleted successfully'}, status=200)


class ManageJoinDaretView(APIAccessMixin, APIView):
    """Manage request to join Darets"""
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id_daret=None, *args, **kwargs):
        """Check if an exist a request to join"""
        user = request.user

        if id_daret:
            # If a specific Daret ID is provided, check the participant's status for that Daret
            daret = get_object_or_404(Daret, pk=id_daret)
            participant_daret = JoinDaret.objects.filter(
                participant=user, daret=daret).first()

            if participant_daret:
                if participant_daret.is_confirmed:
                    return Response({'success': True, 'message': 'You are a confirmed participant in this Daret.'}, status=200)
                else:
                    return Response({'success': False, 'message': 'Your participation is pending confirmation.'}, status=400)
            return Response({'success': False, 'message': 'You are not a participant in this Daret.'}, status=404)

        else:
            # Retrieve all Darets where the user is the owner and has unconfirmed participants
            darets_owned = Daret.objects.filter(owner=user)
            pending_darets = JoinDaret.objects.filter(
                daret__in=darets_owned, is_confirmed=False)

            if pending_darets.exists():
                # Serialize the list of Darets with unconfirmed participants
                daret_data = [
                    {

                        'participant_daret_id': participant_daret.id,
                        'daret': participant_daret.daret.id,
                        'participant_id': participant_daret.participant.id,
                        'daret_name': participant_daret.daret.name,
                        'participant': participant_daret.participant.username,
                        'date_requested': participant_daret.created_at
                    }
                    for participant_daret in pending_darets
                ]

                # Calculate the length of the daret_data
                data_length = len(daret_data)

                return Response({'success': True, 'data': daret_data, 'unreadCount': data_length}, status=200)
            else:
                return Response({'success': False, 'message': 'No Darets with pending participants.'}, status=404)

    def post(self, request, id_daret=None, *args, **kwargs):
        """ Send request to Join an existing Daret as a participant """
        user = request.user

        if id_daret:

            daret = get_object_or_404(Daret, codeGroup=id_daret)

            if not daret:
                return Response({'success': False, 'message': 'This group daret not found'}, status=400)
            # Check if the user is the owner of the Daret
            if daret.owner == user:
                return Response({'success': False, 'message': 'You can not join your own Daret by code.'}, status=400)

            # Check if the user is already a participant
            existing_participant = JoinDaret.objects.filter(
                participant=user, daret=daret).first()
            if existing_participant:
                if existing_participant.is_confirmed:
                    return Response({'success': False, 'message': 'You are already a participant in this Daret'}, status=400)
                else:
                    return Response({'success': False, 'message': 'Your request is pending confirmation from the owner.'}, status=400)

            # Create participant data
            participant_data = {
                "participant": user,
                "daret": daret,
                "is_confirmed": False,  # Request pending confirmation
            }

            serializer = JoinDaretSerializer(data=participant_data)
            if serializer.is_valid():
                serializer.save()

                # Notify the Daret owner of the request
                create_notification(
                    user_source=user,
                    user_destination=daret.owner,
                    message=(
                        "{} {} has requested to join your Daret {}."
                        .format(user.last_name, user.first_name, daret.name)
                    )
                )

                return Response({'success': True, 'message': 'Join request sent, awaiting owner confirmation.'}, status=200)

            return Response({'success': False, 'message': serializer.errors}, status=400)

    def put(self, request, id_daret, *args, **kwargs):
        """Confirm a participant's request to join"""
        user = request.user

        # Retrieve the JoinDaret instance and the associated Daret
        participant_daret = get_object_or_404(JoinDaret, pk=id_daret)
        daret = participant_daret.daret  # Get the Daret directly from JoinDaret

        # Check if the user is the owner of the Daret
        if daret.owner != user:
            return Response({'success': False, 'message': 'You are not authorized to confirm participants in this Daret.'}, status=403)

        # Confirm the participant
        if participant_daret.is_confirmed:  # Optional: Check if already confirmed
            return Response({'success': False, 'message': 'Participant is already confirmed.'}, status=400)

        participant_daret.is_confirmed = True
        participant_daret.save()

        # Adjust number of elements
        daret.nbre_elements += 1
        daret.save()

        # Notify the participant of confirmation
        create_notification(
            user_source=daret.owner,
            user_destination=participant_daret.participant,
            message=(
                "Your request to join the Daret {} has been confirmed."
                .format(daret.name)
            )

        )

        return Response({'success': True, 'message': 'Participant confirmed successfully'}, status=200)

    def delete(self, request, id_daret, *args, **kwargs):
        """Remove request to join a Daret"""
        user = request.user

        participant_daret = get_object_or_404(JoinDaret, pk=id_daret)
        daret = participant_daret.daret
        # daret = get_object_or_404(Daret, pk=participant_daret.daret.pk)

        if daret.owner != user:
            return Response({'success': False, 'message': 'You are not authorized to remove participants from this Daret.'}, status=403)

        # participant_id = request.data.get('participant_id')
        # participant_daret = get_object_or_404(
        #     ParticipantDaret, pk=participant_id, daret=daret)

        participant_daret.delete()

        # Notify the participant of removal
        create_notification(
            user_source=daret.owner,
            user_destination=participant_daret.participant,
            message=(
                "Your request was rejected to join the Daret {}."
                .format(daret.name)
            )

        )

        return Response({'success': True, 'message': 'Participant removed successfully'}, status=200)
