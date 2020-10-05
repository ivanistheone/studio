from __future__ import absolute_import

import uuid

from django.core.urlresolvers import reverse

from contentcuration import models
from contentcuration.tests import testdata
from contentcuration.tests.base import StudioAPITestCase
from contentcuration.viewsets.sync.constants import CHANNELSET
from contentcuration.viewsets.sync.utils import generate_create_event
from contentcuration.viewsets.sync.utils import generate_delete_event
from contentcuration.viewsets.sync.utils import generate_update_event


class SyncTestCase(StudioAPITestCase):
    @property
    def sync_url(self):
        return reverse("sync")

    @property
    def channelset_metadata(self):
        return {
            "id": uuid.uuid4().hex,
            "channels": [self.channel.id],
            "name": "channel set test",
        }

    @property
    def channelset_db_metadata(self):
        return {
            "id": uuid.uuid4().hex,
            "name": "channel set test",
        }

    def setUp(self):
        super(SyncTestCase, self).setUp()
        self.channel = testdata.channel()
        self.user = testdata.user()
        self.channel.editors.add(self.user)

    def test_create_channelset(self):
        self.client.force_authenticate(user=self.user)
        channelset = self.channelset_metadata
        response = self.client.post(
            self.sync_url,
            [generate_create_event(channelset["id"], CHANNELSET, channelset,)],
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        try:
            models.ChannelSet.objects.get(id=channelset["id"])
        except models.ChannelSet.DoesNotExist:
            self.fail("ChannelSet was not created")

    def test_create_channelsets(self):
        self.client.force_authenticate(user=self.user)
        channelset1 = self.channelset_metadata
        channelset2 = self.channelset_metadata
        response = self.client.post(
            self.sync_url,
            [
                generate_create_event(channelset1["id"], CHANNELSET, channelset1,),
                generate_create_event(channelset2["id"], CHANNELSET, channelset2,),
            ],
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        try:
            models.ChannelSet.objects.get(id=channelset1["id"])
        except models.ChannelSet.DoesNotExist:
            self.fail("ChannelSet 1 was not created")

        try:
            models.ChannelSet.objects.get(id=channelset2["id"])
        except models.ChannelSet.DoesNotExist:
            self.fail("ChannelSet 2 was not created")

    def test_update_channelset(self):

        channelset = models.ChannelSet.objects.create(**self.channelset_db_metadata)
        channelset.editors.add(self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.sync_url,
            [generate_update_event(channelset.id, CHANNELSET, {"channels": []},)],
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertFalse(
            models.ChannelSet.objects.get(id=channelset.id)
            .secret_token.channels.filter(pk=self.channel.id)
            .exists()
        )

    def test_update_channelsets(self):

        channelset1 = models.ChannelSet.objects.create(**self.channelset_db_metadata)
        channelset1.editors.add(self.user)
        channelset2 = models.ChannelSet.objects.create(**self.channelset_db_metadata)
        channelset2.editors.add(self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.sync_url,
            [
                generate_update_event(channelset1.id, CHANNELSET, {"channels": []},),
                generate_update_event(channelset2.id, CHANNELSET, {"channels": []},),
            ],
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertFalse(
            models.ChannelSet.objects.get(id=channelset1.id)
            .secret_token.channels.filter(pk=self.channel.id)
            .exists()
        )
        self.assertFalse(
            models.ChannelSet.objects.get(id=channelset2.id)
            .secret_token.channels.filter(pk=self.channel.id)
            .exists()
        )

    def test_update_channelset_empty(self):

        channelset = models.ChannelSet.objects.create(**self.channelset_db_metadata)
        channelset.editors.add(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.sync_url,
            [generate_update_event(channelset.id, CHANNELSET, {},)],
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)

    def test_update_channelset_unwriteable_fields(self):

        channelset = models.ChannelSet.objects.create(**self.channelset_db_metadata)
        channelset.editors.add(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.sync_url,
            [
                generate_update_event(
                    channelset.id, CHANNELSET, {"not_a_field": "not_a_value"},
                )
            ],
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)

    def test_delete_channelset(self):

        channelset = models.ChannelSet.objects.create(**self.channelset_db_metadata)
        channelset.editors.add(self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.sync_url,
            [generate_delete_event(channelset.id, CHANNELSET,)],
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        try:
            models.ChannelSet.objects.get(id=channelset.id)
            self.fail("ChannelSet was not deleted")
        except models.ChannelSet.DoesNotExist:
            pass

    def test_delete_channelsets(self):
        channelset1 = models.ChannelSet.objects.create(**self.channelset_db_metadata)
        channelset2 = models.ChannelSet.objects.create(**self.channelset_db_metadata)
        channelset1.editors.add(self.user)
        channelset2.editors.add(self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.sync_url,
            [
                generate_delete_event(channelset1.id, CHANNELSET,),
                generate_delete_event(channelset2.id, CHANNELSET,),
            ],
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        try:
            models.ChannelSet.objects.get(id=channelset1.id)
            self.fail("ChannelSet 1 was not deleted")
        except models.ChannelSet.DoesNotExist:
            pass

        try:
            models.ChannelSet.objects.get(id=channelset2.id)
            self.fail("ChannelSet 2 was not deleted")
        except models.ChannelSet.DoesNotExist:
            pass


class CRUDTestCase(StudioAPITestCase):
    @property
    def channelset_metadata(self):
        return {
            "id": uuid.uuid4().hex,
            "channels": [self.channel.id],
            "name": "channel set test",
        }

    @property
    def channelset_db_metadata(self):
        return {
            "id": uuid.uuid4().hex,
            "name": "channel set test",
        }

    def setUp(self):
        super(CRUDTestCase, self).setUp()
        self.channel = testdata.channel()
        self.user = testdata.user()
        self.channel.editors.add(self.user)

    def test_create_channelset(self):
        self.client.force_authenticate(user=self.user)
        channelset = self.channelset_metadata
        response = self.client.post(
            reverse("channelset-list"), channelset, format="json",
        )
        self.assertEqual(response.status_code, 201, response.content)
        try:
            models.ChannelSet.objects.get(id=channelset["id"])
        except models.ChannelSet.DoesNotExist:
            self.fail("ChannelSet was not created")

    def test_create_channelset_no_channel_permission(self):
        self.client.force_authenticate(user=self.user)
        new_channel = testdata.channel()
        channelset = self.channelset_metadata
        channelset["channels"] = [new_channel.id]
        response = self.client.post(
            reverse("channelset-list"), channelset, format="json",
        )
        self.assertEqual(response.status_code, 400, response.content)

    def test_update_channelset(self):
        channelset = models.ChannelSet.objects.create(**self.channelset_db_metadata)
        channelset.editors.add(self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse("channelset-detail", kwargs={"pk": channelset.id}),
            {"channels": [self.channel.id]},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(
            models.ChannelSet.objects.get(id=channelset.id)
            .secret_token.channels.filter(pk=self.channel.id)
            .exists()
        )

    def test_update_channelset_empty(self):

        channelset = models.ChannelSet.objects.create(**self.channelset_db_metadata)
        channelset.editors.add(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse("channelset-detail", kwargs={"pk": channelset.id}),
            {},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)

    def test_update_channelset_unwriteable_fields(self):

        channelset = models.ChannelSet.objects.create(**self.channelset_db_metadata)
        channelset.editors.add(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse("channelset-detail", kwargs={"pk": channelset.id}),
            {"not_a_field": "not_a_value"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)

    def test_delete_channelset(self):
        channelset = models.ChannelSet.objects.create(**self.channelset_db_metadata)
        channelset.editors.add(self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            reverse("channelset-detail", kwargs={"pk": channelset.id})
        )
        self.assertEqual(response.status_code, 204, response.content)
        try:
            models.ChannelSet.objects.get(id=channelset.id)
            self.fail("ChannelSet was not deleted")
        except models.ChannelSet.DoesNotExist:
            pass