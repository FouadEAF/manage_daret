from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from authentication.utils import APIAccessMixin
from .models import Tour, ConfirmVirement
from .serializers import TourSerializer, ConfirmVirementSerializer
from daret.models import Daret, JoinDaret
from daret.serializers import DaretSerializer, JoinDaretSerializer
from users.models import User
from notifications.utils import create_notification
import json


class ManageTourView(APIAccessMixin, APIView):
    """Manage Tour in a Daret"""
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id_tour=None, *args, **kwargs):
        """Retrieve one or multiple Tour records"""
        try:
            if id_tour:
                # Get the Daret instance
                daret_instance = get_object_or_404(Daret, id=id_tour)
                # Get all JoinDaret instances related to the Daret
                participants = JoinDaret.objects.filter(
                    daret=daret_instance, is_confirmed=True)
                # Serialize the participants
                serialized_participants = JoinDaretSerializer(
                    participants, many=True)
                return Response({'success': True, 'data': serialized_participants.data}, status=200)
            else:
                # Get all Tour instances
                daret_tours = Tour.objects.all()
                # Serialize the tours
                serialized_daret_tours = TourSerializer(daret_tours, many=True)
                return Response({'success': True, 'data': serialized_daret_tours.data}, status=200)
        except Tour.DoesNotExist:
            return Response({'success': False, 'message': 'Tour not found'}, status=404)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=500)

    def post(self, request, *args, **kwargs):
        """Create or update multiple Tours based on participants"""
        try:
            data = json.loads(request.body)  # Parse the request body
            participants_data = data.get('participants', [])

            if not participants_data:
                return Response({'success': False, 'message': 'No participants data provided'}, status=400)

            for participant in participants_data:
                daret_id = participant.get('daret')
                user_id = participant.get('user')
                date_tour = participant.get('date_obtenu')
                ordre = participant.get('order')

                if not (daret_id and user_id and date_tour and ordre):
                    return Response({'success': False, 'message': 'Missing participant data'}, status=400)

                try:
                    daret_instance = Daret.objects.get(id=daret_id)
                    user_instance = User.objects.get(id=user_id)
                except (Daret.DoesNotExist, User.DoesNotExist) as e:
                    return Response({'success': False, 'message': str(e)}, status=404)

                # Check for existing Tour record
                existing_tour = Tour.objects.filter(
                    daret=daret_instance, user=user_instance).first()

                if existing_tour:
                    existing_tour.date_obtenu = date_tour
                    existing_tour.ordre = ordre
                    existing_tour.save()
                else:
                    # Create new Tour
                    tour_data = {
                        'daret': daret_instance.id,
                        'user': user_instance.id,
                        'date_obtenu': date_tour,
                        'ordre': ordre,
                        'is_recu': False,
                    }
                    serializer = TourSerializer(data=tour_data)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response({'success': False, 'message': serializer.errors}, status=400)

            # Update the Daret's participant count
            daret_instance.nbre_elements = len(participants_data)
            daret_instance.save()

            return Response({'success': True, 'message': 'Tours updated/created successfully'}, status=201)

        except json.JSONDecodeError:
            return Response({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=500)

    def put(self, request, id_tour, *args, **kwargs):
        """Update an existing Tour"""
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({'success': False, 'message': 'Invalid JSON data'}, status=400)

        if not id_tour:
            return Response({'success': False, 'message': 'Tour ID is required'}, status=400)

        try:
            tour = Tour.objects.get(pk=id_tour)
            serializer = TourSerializer(tour, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, 'message': 'Tour updated successfully'}, status=200)
            return Response({'success': False, 'message': serializer.errors}, status=400)
        except Tour.DoesNotExist:
            return Response({'success': False, 'message': 'Tour not found'}, status=404)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=500)

    def delete(self, request, id_tour, *args, **kwargs):
        """Delete a specific Tour"""
        try:
            if not id_tour:
                return Response({'success': False, 'message': 'Tour ID is required'}, status=400)

            tour = Tour.objects.filter(pk=id_tour).delete()
            if tour[0]:
                return Response({'success': True, 'message': 'Tour deleted successfully'}, status=200)
            else:
                return Response({'success': False, 'message': 'Tour not found'}, status=404)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=500)


class ManageConfirmVirementView(APIAccessMixin, APIView):
    """Manage ConfirmVirement records"""
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id_confirm_virement=None, *args, **kwargs):
        """Retrieve one or multiple ConfirmVirement records"""
        try:
            user = request.user

            if id_confirm_virement:
                confirm_virement_instance = get_object_or_404(
                    ConfirmVirement, id=id_confirm_virement)
                serialized_data = ConfirmVirementSerializer(
                    confirm_virement_instance)
                return Response({'success': True, 'data': serialized_data.data}, status=200)
            else:
                if not user.is_authenticated:
                    return Response({'success': False, 'message': 'User not authenticated.'}, status=403)

                confirm_virement_instances = ConfirmVirement.objects.filter(
                    partie_beneficiaire=user.id, is_send=False)

                if not confirm_virement_instances.exists():
                    return Response({'success': False, 'message': 'No records found.'}, status=200)

                serialized_data = ConfirmVirementSerializer(
                    confirm_virement_instances, many=True)
                return Response({'success': True, 'data': serialized_data.data, 'unreadCount': len(serialized_data.data)}, status=200)
        except ConfirmVirement.DoesNotExist:
            return Response({'success': False, 'message': 'Confirm Virement not found'}, status=404)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=500)

    def post(self, request, *args, **kwargs):
        """Create a new ConfirmVirement"""
        try:
            data = json.loads(request.body)
            tour_id = data.get('tour')
            partie_beneficiaire_username = data.get('partie_beneficiaire')
            partie_donnenant_username = data.get('partie_donnenant')

            tour = get_object_or_404(Tour, pk=tour_id)
            partie_beneficiaire = get_object_or_404(
                User, username=partie_beneficiaire_username)
            partie_donnenant = get_object_or_404(
                User, username=partie_donnenant_username)

            virement_data = {
                'tour': tour.id,
                'partie_beneficiaire': partie_beneficiaire.id,
                'partie_donnenant': partie_donnenant.id
            }

            if ConfirmVirement.objects.filter(tour=tour, partie_beneficiaire=partie_beneficiaire, partie_donnenant=partie_donnenant).exists():
                return Response({'success': False, 'message': 'You already sent money.'}, status=400)

            serializer = ConfirmVirementSerializer(data=virement_data)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, 'message': 'Confirm Virement created successfully'}, status=201)
            return Response({'success': False, 'message': serializer.errors}, status=400)
        except json.JSONDecodeError:
            return Response({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=500)

    def put(self, request, id_confirm_virement, *args, **kwargs):
        """Update an existing ConfirmVirement"""
        if not id_confirm_virement:
            return Response({'success': False, 'message': 'Confirm Virement ID is required'}, status=400)

        try:
            confirm_virement = ConfirmVirement.objects.get(
                pk=id_confirm_virement)
            confirm_virement.is_send = True
            confirm_virement.save()

            create_notification(
                user_source=confirm_virement.partie_beneficiaire,
                user_destination=confirm_virement.partie_donnenant,
                message=(
                    "Mr {} confirmed that they received money."
                    .format(confirm_virement.partie_beneficiaire_full_name)
                )

            )

            return Response({'success': True, 'message': 'Confirm Virement updated successfully'}, status=200)
        except ConfirmVirement.DoesNotExist:
            return Response({'success': False, 'message': 'Confirm Virement not found'}, status=404)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=500)

    def delete(self, request, id_confirm_virement, *args, **kwargs):
        """Delete a ConfirmVirement"""
        try:
            if not id_confirm_virement:
                return Response({'success': False, 'message': 'Confirm Virement ID is required'}, status=400)

            confirm_virement = ConfirmVirement.objects.filter(
                pk=id_confirm_virement).delete()

            if confirm_virement[0]:
                return Response({'success': True, 'message': 'Confirm Virement deleted successfully'}, status=200)
            else:
                return Response({'success': False, 'message': 'Confirm Virement not found'}, status=404)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=500)
