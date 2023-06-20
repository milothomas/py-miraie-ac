"""Custom exceptions"""
class AuthException(Exception):
    """Custom exception to indicate authentication failure"""

class ConnectionException(Exception):
    """Custom exception to indicate connection failure"""

class MobileNotRegisteredException(Exception):
    """Custom exception to indicate that the mobile number has not been registered with MirAIe servers"""
