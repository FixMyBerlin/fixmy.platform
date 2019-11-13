from django.test import Client, TestCase
from .models import Rating, Scene
import json
import uuid


class ViewsTest(TestCase):

    fixtures = ['scenes']

    def setUp(self):
        self.client = Client()
        self.profile = {
            'ageGroup': 1,
            'berlinTraffic': 3,
            'bicycleUse': 0,
            'bikeReasons': ['skills', 'social'],
            'bikeReasonsVar': 'Tja',
            'district': 'Mitte',
            'gender': 'd',
            'hasChildren': True,
            'isTosAccepted': True,
            'motivationalFactors': {
                'bikeFun': 4,
                'faster': 4,
                'weather': 4,
                'safe': 4
            },
            'transportRatings': {
                'pedelec': 0,
                'bicycle': 5,
                'motorbike': 3,
                'car': 0,
                'public': 3
            },
            'userGroup': 'car',
            'perspective': 'car',
            'vehiclesOwned': ['car'],
            'whyBiking': ['social'],
            'zipcode': '22000'
        }
        self.session = uuid.uuid4()

    def test_add_survey(self):
        response = self.client.put(
            '/api/survey/1/{}'.format(self.session),
            data=json.dumps(self.profile),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json().get('ratings_total'), 0)
        self.assertEqual(len(response.json().get('scenes', [])), 5)

        ratings = Rating.objects.filter(survey=self.session).all()
        self.assertEqual(len(ratings), 5)

    def test_add_rating(self):
        response = self.client.put(
            '/api/survey/1/{}'.format(self.session),
            data=json.dumps(self.profile),
            content_type='application/json'
        )
        scenes = response.json().get('scenes')
        data = {
            'sceneID': scenes[0],
            'duration': 2187,
            'rating': 2
        }
        response = self.client.put(
            '/api/survey/1/{}/ratings/{}'.format(self.session, scenes[0]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)

        scene = Scene.find_by_scene_id(scenes[0])
        rating = Rating.objects.get(survey=self.session, scene=scene)
        self.assertEqual(rating.rating, data['rating'])
        self.assertEqual(rating.duration, data['duration'])

    def test_add_perspective(self):
        self.client.put(
            '/api/survey/1/{}'.format(self.session),
            data=json.dumps(self.profile),
            content_type='application/json'
        )
        response = self.client.post(
            '/api/survey/1/{}'.format(self.session),
            data=json.dumps({'perspective': 'bicycle'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('ratings_total'), 0)
        self.assertEqual(len(response.json().get('scenes', [])), 10)
