from tests.app.helpers import BaseApplicationTest
from flask import json
from datetime import datetime
from app.models import AuditEvent
from app import db
from dmutils.audit import AuditTypes

from nose.tools import assert_equal, assert_in


class TestAudits(BaseApplicationTest):
    def setup(self):
        super(TestAudits, self).setup()

    @staticmethod
    def audit_event(user, type):
        return AuditEvent(
            audit_type=type,
            db_object=None,
            user=user,
            data={'request': "data"}
        )

    def add_audit_events(self, number, type=AuditTypes.supplier_update):
        with self.app.app_context():
            for i in range(number):
                db.session.add(
                    self.audit_event(i, type)
                )
            db.session.commit()

    def test_should_get_audit_event(self):
        self.add_audit_events(1)
        response = self.client.get('/audit-events')
        data = json.loads(response.get_data())

        assert_equal(response.status_code, 200)
        assert_equal(len(data['auditEvents']), 1)
        assert_equal(data['auditEvents'][0]['user'], '0')
        assert_equal(data['auditEvents'][0]['data']['request'], 'data')

    def test_should_get_audit_event_using_audit_date(self):
        today = datetime.now().strftime("%Y-%m-%d")

        self.add_audit_events(1)
        response = self.client.get('/audit-events?audit-date={}'.format(today))
        data = json.loads(response.get_data())

        assert_equal(response.status_code, 200)
        assert_equal(len(data['auditEvents']), 1)
        assert_equal(data['auditEvents'][0]['user'], '0')
        assert_equal(data['auditEvents'][0]['data']['request'], 'data')

    def test_should_not_get_audit_event_for_date_with_no_events(self):
        self.add_audit_events(1)
        response = self.client.get('/audit-events?audit-date=2000-01-01')
        data = json.loads(response.get_data())

        assert_equal(response.status_code, 200)
        assert_equal(len(data['auditEvents']), 0)

    def test_should_reject_invalid_audit_dates(self):
        self.add_audit_events(1)
        response = self.client.get('/audit-events?audit-date=invalid')

        assert_equal(response.status_code, 400)

    def test_should_get_audit_event_by_type(self):
        self.add_audit_events(1, AuditTypes.contact_update)
        self.add_audit_events(1, AuditTypes.supplier_update)
        response = self.client.get('/audit-events?audit-type=contact_update')
        data = json.loads(response.get_data())

        assert_equal(response.status_code, 200)
        assert_equal(len(data['auditEvents']), 1)
        assert_equal(data['auditEvents'][0]['user'], '0')
        assert_equal(data['auditEvents'][0]['type'], 'contact_update')
        assert_equal(data['auditEvents'][0]['data']['request'], 'data')

    def test_should_reject_invalid_audit_type(self):
        self.add_audit_events(1)
        response = self.client.get('/audit-events?audit-type=invalid')

        assert_equal(response.status_code, 400)

    def test_should_get_audit_events_ordered_by_created_date(self):
        self.add_audit_events(5)
        response = self.client.get('/audit-events')
        data = json.loads(response.get_data())

        assert_equal(response.status_code, 200)
        assert_equal(len(data['auditEvents']), 5)

        assert_equal(data['auditEvents'][4]['user'], '4')
        assert_equal(data['auditEvents'][3]['user'], '3')
        assert_equal(data['auditEvents'][2]['user'], '2')
        assert_equal(data['auditEvents'][1]['user'], '1')
        assert_equal(data['auditEvents'][0]['user'], '0')

    def test_should_reject_invalid_page(self):
        self.add_audit_events(1)
        response = self.client.get('/audit-events?page=invalid')

        assert_equal(response.status_code, 400)

    def test_should_reject_missing_page(self):
        self.add_audit_events(1)
        response = self.client.get('/audit-events?page=')

        assert_equal(response.status_code, 400)

    def test_should_return_404_if_page_exceeds_results(self):
        self.add_audit_events(7)
        response = self.client.get('/audit-events?page=100')

        assert_equal(response.status_code, 404)

    def test_should_get_audit_events_paginated(self):
        self.add_audit_events(7)
        response = self.client.get('/audit-events')
        data = json.loads(response.get_data())

        assert_equal(response.status_code, 200)
        assert_equal(len(data['auditEvents']), 5)
        next_link = data['links']['next']
        assert_in('page=2', next_link)
        assert_equal(data['auditEvents'][0]['user'], '0')
        assert_equal(data['auditEvents'][1]['user'], '1')
        assert_equal(data['auditEvents'][2]['user'], '2')
        assert_equal(data['auditEvents'][3]['user'], '3')
        assert_equal(data['auditEvents'][4]['user'], '4')

    def test_paginated_audit_events_page_two(self):
        self.add_audit_events(7)

        response = self.client.get('/audit-events?page=2')
        data = json.loads(response.get_data())

        assert_equal(response.status_code, 200)
        assert_equal(len(data['auditEvents']), 2)
        prev_link = data['links']['prev']
        assert_in('page=1', prev_link)
        assert_equal(data['auditEvents'][0]['user'], '5')
        assert_equal(data['auditEvents'][1]['user'], '6')

    def test_reject_invalid_audit_id_on_acknowledgement(self):
        res = self.client.post(
            '/audit-events/invalid-id!/acknowledge',
            data=json.dumps({'key': 'value'}),
            content_type='application/json')

        assert_equal(res.status_code, 404)

    def test_reject_if_no_updater_details_on_acknowledgement(self):
        res = self.client.post(
            '/audit-events/123/acknowledge',
            data={},
            content_type='application/json')

        assert_equal(res.status_code, 400)

    def test_should_update_audit_event(self):
        self.add_audit_events(1)
        response = self.client.get('/audit-events')
        data = json.loads(response.get_data())

        res = self.client.post(
            '/audit-events/{}/acknowledge'.format(
                data['auditEvents'][0]['id']
            ),
            data=json.dumps({
                'update_details': {'updated_by': 'tests'}
            }),
            content_type='application/json')
        # re-fetch to get updated data
        new_response = self.client.get('/audit-events')
        new_data = json.loads(new_response.get_data())
        assert_equal(res.status_code, 200)
        assert_equal(new_data['auditEvents'][0]['acknowledged'], True)
        assert_equal(new_data['auditEvents'][0]['acknowledgedBy'], 'tests')

    def test_should_get_all_audit_events(self):
        self.add_audit_events(2)
        response = self.client.get('/audit-events')
        data = json.loads(response.get_data())

        res = self.client.post(
            '/audit-events/{}/acknowledge'.format(
                data['auditEvents'][0]['id']
            ),
            data=json.dumps({
                'update_details': {'updated_by': 'tests'}
            }),
            content_type='application/json')
        # re-fetch to get updated data
        new_response = self.client.get('/audit-events')
        new_data = json.loads(new_response.get_data())
        assert_equal(res.status_code, 200)
        assert_equal(len(new_data['auditEvents']), 2)

        # all should return both
        new_response = self.client.get('/audit-events?acknowledged=all')
        new_data = json.loads(new_response.get_data())
        assert_equal(res.status_code, 200)
        assert_equal(len(new_data['auditEvents']), 2)

    def test_should_get_only_acknowledged_audit_events(self):
        self.add_audit_events(2)
        response = self.client.get('/audit-events')
        data = json.loads(response.get_data())

        res = self.client.post(
            '/audit-events/{}/acknowledge'.format(
                data['auditEvents'][0]['id']
            ),
            data=json.dumps({
                'update_details': {'updated_by': 'tests'}
            }),
            content_type='application/json')
        # re-fetch to get updated data
        new_response = self.client.get(
            '/audit-events?acknowledged=true'
        )
        new_data = json.loads(new_response.get_data())
        assert_equal(res.status_code, 200)
        assert_equal(len(new_data['auditEvents']), 1)
        assert_equal(
            new_data['auditEvents'][0]['id'],
            data['auditEvents'][0]['id'])

    def test_should_get_only_not_acknowledged_audit_events(self):
        self.add_audit_events(2)
        response = self.client.get('/audit-events')
        data = json.loads(response.get_data())

        res = self.client.post(
            '/audit-events/{}/acknowledge'.format(
                data['auditEvents'][0]['id']
            ),
            data=json.dumps({
                'update_details': {'updated_by': 'tests'}
            }),
            content_type='application/json')
        # re-fetch to get updated data
        new_response = self.client.get(
            '/audit-events?acknowledged=false'
        )
        new_data = json.loads(new_response.get_data())
        assert_equal(res.status_code, 200)
        assert_equal(len(new_data['auditEvents']), 1)
        assert_equal(
            new_data['auditEvents'][0]['id'],
            data['auditEvents'][1]['id']
        )
