import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from whatsapp_groups.models import WhatsAppGroup


@csrf_exempt
def group_lifecycle_webhook(request):
    """
    Handle WhatsApp group lifecycle webhooks.
    
    GET: Webhook verification (WhatsApp requires this)
    POST: Receive webhook events from WhatsApp
    
    Webhook URL: /api/webhooks/group-lifecycle/
    """
    # Handle GET request for webhook verification
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        # Set your verify token in settings.py: WHATSAPP_WEBHOOK_VERIFY_TOKEN
        verify_token = getattr(settings, 'WHATSAPP_WEBHOOK_VERIFY_TOKEN', 'your_verify_token_here')
        
        if mode == 'subscribe' and token == verify_token:
            print("✅ Webhook verified successfully")
            return HttpResponse(challenge, status=200)
        else:
            print(f"❌ Webhook verification failed: mode={mode}, token={token}")
            return HttpResponse('Verification failed', status=403)
    
    # Handle POST request for webhook events
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Log webhook for debugging
        print("=" * 60)
        print("WHATSAPP WEBHOOK RECEIVED:")
        print(json.dumps(data, indent=2))
        print("=" * 60)
        
        # Extract webhook data - Real WhatsApp format
        entry = data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        field = changes.get('field')
        
        # Handle group lifecycle update
        if field == 'group_lifecycle_update' or 'group' in value:
            # Real WhatsApp webhook format
            group_data = value.get('group', {})
            group_id = group_data.get('id')
            request_id = group_data.get('request_id')
            creation_status = group_data.get('creation_status')
            subject = group_data.get('subject')
            
            # Find the group by request_id (most reliable)
            group = None
            if request_id:
                try:
                    group = WhatsAppGroup.objects.filter(request_id=request_id, status='pending').first()
                except WhatsAppGroup.DoesNotExist:
                    pass
            
            # If not found by request_id, try by group_id
            if not group and group_id:
                try:
                    group = WhatsAppGroup.objects.get(group_id=group_id)
                except WhatsAppGroup.DoesNotExist:
                    pass
            
            # If still not found, log and return
            if not group:
                return JsonResponse({
                    'status': 'received',
                    'message': 'Group not found in database',
                    'group_id': group_id,
                    'request_id': request_id,
                    'creation_status': creation_status
                }, status=200)
            
            # Handle different creation statuses
            if creation_status == 'GROUP_CREATED':
                # Update group with group_id from webhook
                if group_id:
                    group.group_id = group_id
                if subject and not group.subject:
                    group.subject = subject
                
                # Check if invite_link is in webhook (may be in different location)
                invite_link = group_data.get('invite_link') or value.get('invite_link')
                if invite_link:
                    group.invite_link = invite_link
                
                group.status = 'created'
                group.save()
                
                print(f"✅ Group updated: ID={group.id}, Group ID={group_id}, Status=created")
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Group created successfully',
                    'group_id': group_id,
                    'request_id': request_id
                }, status=200)
            
            elif creation_status == 'GROUP_CREATE_FAILED' or creation_status == 'FAILED':
                error_message = group_data.get('error', {}).get('message', 'Group creation failed')
                group.status = 'failed'
                group.error_message = error_message
                group.save()
                
                print(f"❌ Group creation failed: ID={group.id}, Error={error_message}")
                
                return JsonResponse({
                    'status': 'error',
                    'message': 'Group creation failed',
                    'error': error_message,
                    'request_id': request_id
                }, status=200)
            
            else:
                # Unknown status, log it
                print(f"⚠️ Unknown creation_status: {creation_status}")
                return JsonResponse({
                    'status': 'received',
                    'message': f'Unknown creation status: {creation_status}',
                    'creation_status': creation_status
                }, status=200)
        
        # Handle other webhook types (messages, status updates, etc.)
        # You can add handlers here for other webhook types
        
        return JsonResponse({
            'status': 'received',
            'message': 'Webhook received but no action taken'
        }, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

