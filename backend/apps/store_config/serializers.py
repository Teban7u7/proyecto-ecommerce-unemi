from rest_framework import serializers
from .models import StoreConfig


class StoreConfigSerializer(serializers.ModelSerializer):
    active_credentials = serializers.SerializerMethodField()
    checkout_conf = serializers.SerializerMethodField()

    class Meta:
        model = StoreConfig
        fields = (
            'store_name', 'environment',
            'iva_percentage', 'default_installments_type',
            'checkout_logo_url', 'checkout_primary_color',
            'whatsapp_number',
            'webhook_url', 'success_url', 'failure_url', 'pending_url',
            'active_credentials', 'checkout_conf', 'updated_at',
        )
        read_only_fields = ('active_credentials', 'checkout_conf', 'updated_at')

    def get_active_credentials(self, obj):
        creds = obj.get_active_credentials()
        # Mask the keys for security
        return {
            'environment': obj.environment,
            'app_code_client': creds['app_code_client'],
            'app_key_client': creds['app_key_client'], # Client key is safe to expose
            'app_code_server': creds['app_code_server'],
            'ccapi_url': creds['ccapi_url'],
            'noccapi_url': creds['noccapi_url'],
            'has_server_key': bool(creds['app_key_server']),
        }

    def get_checkout_conf(self, obj):
        return obj.get_checkout_conf()


class EnvironmentSwitchSerializer(serializers.Serializer):
    """Serializer for switching between STG and PROD."""
    environment = serializers.ChoiceField(choices=StoreConfig.Environment.choices)
