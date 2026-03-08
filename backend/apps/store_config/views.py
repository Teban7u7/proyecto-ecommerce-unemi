from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import StoreConfig
from .serializers import StoreConfigSerializer, EnvironmentSwitchSerializer


class StoreConfigView(APIView):
    """Get and update store configuration."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        config = StoreConfig.get_config()
        return Response(StoreConfigSerializer(config).data)

    def put(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        config = StoreConfig.get_config()
        serializer = StoreConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class EnvironmentSwitchView(APIView):
    """
    Switch between STG and PROD environments.
    This is the one-click switch that changes all Nuvei endpoints.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = EnvironmentSwitchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        config = StoreConfig.get_config()
        new_env = serializer.validated_data['environment']
        old_env = config.environment

        config.environment = new_env
        config.save()

        creds = config.get_active_credentials()

        return Response({
            'message': f'Ambiente cambiado de {old_env} a {new_env}',
            'environment': new_env,
            'ccapi_url': creds['ccapi_url'],
            'noccapi_url': creds['noccapi_url'],
            'app_code_server': creds['app_code_server'],
            'has_server_key': bool(creds['app_key_server']),
        })

    def get(self, request):
        """Get current environment status."""
        config = StoreConfig.get_config()
        return Response({
            'environment': config.environment,
            'environment_display': config.get_environment_display(),
        })
