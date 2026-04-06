from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class RecordThrottle(UserRateThrottle):
    scope = 'records'


class LoginThrottle(AnonRateThrottle):
    scope = 'login'