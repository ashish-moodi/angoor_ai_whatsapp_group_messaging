import requests
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from whatsapp_groups.models import WhatsAppGroup
from whatsapp_groups.serializers import WhatsAppGroupSerializer, CreateGroupRequestSerializer


@api_view(['POST'])
def create_group(request):
    serializer = CreateGroupRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    business_phone_number_id = settings.WHATSAPP_BUSINESS_PHONE_NUMBER_ID
    api_url = f"{settings.WHATSAPP_API_BASE_URL}/{business_phone_number_id}/groups"

    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "subject": validated_data['subject'],
    }
    
    if validated_data.get('description'):
        payload['description'] = validated_data['description']
    
    if validated_data.get('join_approval_mode'):
        payload['join_approval_mode'] = validated_data['join_approval_mode']
    
    group = WhatsAppGroup.objects.create(
        subject=validated_data['subject'],
        description=validated_data.get('description', ''),
        join_approval_mode=validated_data.get('join_approval_mode', WhatsAppGroup.JoinApprovalMode.AUTO_APPROVE),
        business_phone_number="919205311559",
        status='pending'
    )
    
    try:
        # Make API call to WhatsApp
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            
            request_id = response_data.get('request_id')
            if request_id:
                group.request_id = request_id
                group.status = 'pending'  # Keep as pending until webhook confirms
            
            if 'id' in response_data:
                group.group_id = response_data.get('id')
                group.status = 'created'
            
            if 'invite_link' in response_data:
                group.invite_link = response_data['invite_link']
            
            group.save()
            
            return Response(
                {
                    'message': 'Group created successfully',
                    'group': WhatsAppGroupSerializer(group).data,
                    'whatsapp_response': response_data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            # Update group with error status
            error_message = response.text
            try:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', error_message)
            except:
                pass
            
            group.status = 'failed'
            group.error_message = error_message
            group.save()
            
            return Response(
                {
                    'message': 'Failed to create group',
                    'error': error_message,
                    'group': WhatsAppGroupSerializer(group).data
                },
                status=response.status_code
            )
            
    except requests.exceptions.RequestException as e:
        # Update group with error status
        group.status = 'failed'
        group.error_message = str(e)
        group.save()
        
        return Response(
            {
                'message': 'Error connecting to WhatsApp API',
                'error': str(e),
                'group': WhatsAppGroupSerializer(group).data
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def list_groups(request):
    groups = WhatsAppGroup.objects.all()
    serializer = WhatsAppGroupSerializer(groups, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_group(request, group_id):
    try:
        group = WhatsAppGroup.objects.get(id=group_id)
        serializer = WhatsAppGroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except WhatsAppGroup.DoesNotExist:
        return Response(
            {'error': 'Group not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def get_group_join_requests(request, group_id):
    
    try:
        group = WhatsAppGroup.objects.get(id=group_id)
        print(f"✅ Group found in database:")
        print(f"   DB ID: {group.id}")
        print(f"   WhatsApp Group ID: {group.group_id}")
        print(f"   Subject: {group.subject}")
        print(f"   Status: {group.status}")
        print(f"   Join Mode: {group.join_approval_mode}")
    except WhatsAppGroup.DoesNotExist:
        return Response(
            {'error': 'Group not found'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not group.group_id:
        return Response(
            {'error': 'WhatsApp group_id not available yet for this group'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    api_url = f"{settings.WHATSAPP_API_BASE_URL}/{group.group_id}/join_requests"
    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=30)

        if response.status_code == 200:
            return Response(
                {
                    'message': 'Join requests fetched successfully',
                    'group': WhatsAppGroupSerializer(group).data,
                    'whatsapp_response': response.json(),
                },
                status=status.HTTP_200_OK,
            )
        else:
            error_message = response.text
            try:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', error_message)
            except Exception:
                pass

            return Response(
                {
                    'message': 'Failed to fetch join requests',
                    'error': error_message,
                },
                status=response.status_code,
            )
    except requests.exceptions.RequestException as e:
        return Response(
            {
                'message': 'Error connecting to WhatsApp API',
                'error': str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
def approve_group_join_requests(request, group_id):
    try:
        group = WhatsAppGroup.objects.get(id=group_id)
    except WhatsAppGroup.DoesNotExist:
        return Response(
            {'error': 'Group not found'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not group.group_id:
        return Response(
            {'error': 'WhatsApp group_id not available yet for this group'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    join_requests = request.data.get('join_requests')
    if not isinstance(join_requests, list) or not join_requests:
        return Response(
            {'error': 'join_requests must be a non-empty list of join request IDs'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    api_url = f"{settings.WHATSAPP_API_BASE_URL}/{group.group_id}/join_requests"
    payload = {
        "messaging_product": "whatsapp",
        "join_requests": join_requests,
    }
    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            return Response(
                {
                    'message': 'Join requests approved successfully',
                    'group': WhatsAppGroupSerializer(group).data,
                    'whatsapp_response': response.json(),
                },
                status=status.HTTP_200_OK,
            )
        else:
            error_message = response.text
            try:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', error_message)
            except Exception:
                pass

            return Response(
                {
                    'message': 'Failed to approve join requests',
                    'error': error_message,
                },
                status=response.status_code,
            )
    except requests.exceptions.RequestException as e:
        return Response(
            {
                'message': 'Error connecting to WhatsApp API',
                'error': str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
def reject_group_join_requests(request, group_id):
    try:
        group = WhatsAppGroup.objects.get(id=group_id)
    except WhatsAppGroup.DoesNotExist:
        return Response(
            {'error': 'Group not found'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not group.group_id:
        return Response(
            {'error': 'WhatsApp group_id not available yet for this group'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    join_requests = request.data.get('join_requests')
    if not isinstance(join_requests, list) or not join_requests:
        return Response(
            {'error': 'join_requests must be a non-empty list of join request IDs'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    api_url = f"{settings.WHATSAPP_API_BASE_URL}/{group.group_id}/join_requests"
    payload = {
        "messaging_product": "whatsapp",
        "join_requests": join_requests,
    }
    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.delete(api_url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            return Response(
                {
                    'message': 'Join requests rejected successfully',
                    'group': WhatsAppGroupSerializer(group).data,
                    'whatsapp_response': response.json(),
                },
                status=status.HTTP_200_OK,
            )
        else:
            error_message = response.text
            try:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', error_message)
            except Exception:
                pass

            return Response(
                {
                    'message': 'Failed to reject join requests',
                    'error': error_message,
                },
                status=response.status_code,
            )
    except requests.exceptions.RequestException as e:
        return Response(
            {
                'message': 'Error connecting to WhatsApp API',
                'error': str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

