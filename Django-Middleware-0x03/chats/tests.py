from django.test import TestCase
from django.http import HttpResponse
from django.utils import timezone

from chats import middleware


class DummyUser:
	def __init__(self, username='tester', email='tester@example.com', role='guest'):
		self.username = username
		self.email = email
		self.role = role


class DummyRequest:
	def __init__(self, method='GET', path='/', ip='127.0.0.1', user=None):
		self.method = method
		self.path = path
		self.META = {'REMOTE_ADDR': ip}
		self.user = user or DummyUser()


class MiddlewareTests(TestCase):
	"""Unit tests for the custom chat middleware."""

	def test_request_logging_middleware_writes_log(self):
		# Prepare
		request = DummyRequest(method='GET', path='/test-path')
		called = {'ok': False}

		def get_response(req):
			called['ok'] = True
			return HttpResponse('ok')

		mw = middleware.RequestLoggingMiddleware(get_response)

		# Act
		response = mw(request)

		# Assert
		self.assertTrue(called['ok'])
		# Ensure the log file contains the path
		with open('Django-Middleware-0x03/chats/requests.log', 'r') as f:
			content = f.read()
		self.assertIn('/test-path', content)

	def test_restrict_access_by_time_blocks_out_of_hours(self):
		request = DummyRequest(method='GET', path='/')

		# Force time to an hour outside allowed range (e.g., 23:00)
		class FakeDateTime:
			@classmethod
			def now(cls):
				return timezone.datetime(2025, 1, 1, 23, 0, 0)

		# Monkeypatch the module's datetime to this fake one
		orig_dt = middleware.datetime
		try:
			middleware.datetime = FakeDateTime
			mw = middleware.RestrictAccessByTimeMiddleware(lambda r: HttpResponse('ok'))
			res = mw(request)
			self.assertEqual(res.status_code, 403)
		finally:
			middleware.datetime = orig_dt

	def test_offensive_language_rate_limit(self):
		request = DummyRequest(method='POST', path='/')
		mw = middleware.OffensiveLanguageMiddleware(lambda r: HttpResponse('ok'), limit=3, window_seconds=60)

		# first 3 requests should pass
		for _ in range(3):
			res = mw(request)
			# middleware returns HttpResponse only if allowed
			self.assertEqual(res.status_code, 200)

		# fourth should be forbidden
		res = mw(request)
		self.assertEqual(res.status_code, 403)

	def test_role_permission_blocks_non_admin(self):
		guest_request = DummyRequest(method='DELETE', path='/manage/resource', user=DummyUser(role='guest'))
		mw = middleware.RolePermissionMiddleware(lambda r: HttpResponse('ok'))
		res = mw(guest_request)
		self.assertEqual(res.status_code, 403)

		admin_request = DummyRequest(method='DELETE', path='/manage/resource', user=DummyUser(role='admin'))
		res = mw(admin_request)
		self.assertEqual(res.status_code, 200)
