import json

import pytest
from django.conf import settings

from kubeportal.k8s import kubernetes_api as api
from kubeportal.models import KubernetesNamespace
from kubeportal.tests.helpers import run_minikube_sync, apply_k8s_yml, minikube_unavailable
from kubeportal.tests.test_api import BASE_DIR


@pytest.mark.django_db
def test_ingresses_denied(api_client_anon):
    response = api_client_anon.post(f'/api/{settings.API_VERSION}/namespaces/default/ingresses/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_ingresshosts_denied(api_client_anon):
    response = api_client_anon.get(f'/api/{settings.API_VERSION}/ingresshosts/')
    assert response.status_code == 401


@pytest.mark.skipif(minikube_unavailable(), reason="Minikube is unavailable")
def test_user_ingresses_create(api_client, admin_user):
    run_minikube_sync()
    system_namespace = KubernetesNamespace.objects.get(name="kube-system")
    admin_user.service_account = system_namespace.service_accounts.all()[0]
    admin_user.save()
    try:
        response = api_client.post(f'/api/{settings.API_VERSION}/namespaces/kube-system/ingresses/',
                                   {
                                       'name': 'my-ingress',
                                       'annotations': [
                                           {'key': 'nginx.ingress.kubernetes.io/rewrite-target', 'value': '/'}
                                       ],
                                       'tls': True,
                                       'rules': [
                                           {'host': 'www.example.com',
                                            'paths': [
                                                {'path': '/svc',
                                                 'service_name': 'my-svc',
                                                 'service_port': 8000
                                                 },
                                                {'path': '/docs',
                                                 'service_name': 'my-docs-svc',
                                                 'service_port': 5000
                                                 }
                                            ]
                                            }
                                       ]
                                   })

        assert 201 == response.status_code
    finally:
        api.get_portal_net_v1().delete_namespaced_ingress(name="my-ingress", namespace="kube-system")


@pytest.mark.skipif(minikube_unavailable(), reason="Minikube is unavailable")
def test_user_ingresses_create_empty_path(api_client, admin_user):
    run_minikube_sync()
    system_namespace = KubernetesNamespace.objects.get(name="kube-system")
    admin_user.service_account = system_namespace.service_accounts.all()[0]
    admin_user.save()
    try:
        response = api_client.post(f'/api/{settings.API_VERSION}/namespaces/kube-system/ingresses/',
                                   {
                                       'name': 'my-ingress',
                                       'rules': [
                                           {'host': 'www.example.com',
                                            'paths': [
                                                {'service_name': 'my-svc1',
                                                 'service_port': 8000
                                                 },
                                                {'path': '',
                                                 'service_name': 'my-svc2',
                                                 'service_port': 5000
                                                 },
                                                {'path': '/',
                                                 'service_name': 'my-svc3',
                                                 'service_port': 5000
                                                 }
                                            ]
                                            }
                                       ]
                                   })
        assert 201 == response.status_code

        response = api_client.get(f'/api/{settings.API_VERSION}/namespaces/kube-system/')
        assert 200 == response.status_code
        data = json.loads(response.content)
        from urllib.parse import urlparse
        ingresses_url = urlparse(data['ingresses_url'])

        response = api_client.get(ingresses_url.path)
        assert 200 == response.status_code
        data = json.loads(response.content)
        ingress_url = urlparse(data['ingress_urls'][0])

        response = api_client.get(ingress_url.path)
        assert 200 == response.status_code
        data = json.loads(response.content)

        assert data['rules'][0]['paths'][0]['path'] == ''
        assert data['rules'][0]['paths'][1]['path'] == ''
        assert data['rules'][0]['paths'][2]['path'] == '/'
    finally:
        api.get_portal_net_v1().delete_namespaced_ingress(name="my-ingress", namespace="kube-system")


def test_user_ingresses_create_wrong_ns(api_client):
    response = api_client.post(f'/api/{settings.API_VERSION}/namespaces/xyz/ingresses/',
                               {
                                   'name': 'my-ingress',
                                   'annotations': [
                                       {'key': 'nginx.ingress.kubernetes.io/rewrite-target', 'value': '/'}
                                   ],
                                   'tls': True,
                                   'rules': [
                                       {'host': 'www.example.com',
                                        'paths': [
                                            {'path': '/svc',
                                             'service_name': 'my-svc',
                                             'service_port': 8000
                                             },
                                            {'path': '/docs',
                                             'service_name': 'my-docs-svc',
                                             'service_port': 5000
                                             }
                                        ]
                                        }
                                   ]
                               })
    assert 404 == response.status_code


@pytest.mark.skipif(minikube_unavailable(), reason="Minikube is unavailable")
def test_user_ingresses_list(api_client, admin_user_with_k8s):
    apply_k8s_yml(BASE_DIR + "fixtures/ingress1.yml")
    apply_k8s_yml(BASE_DIR + "fixtures/ingress2.yml")

    try:
        response = api_client.get(f'/api/{settings.API_VERSION}/namespaces/default/')
        assert 200 == response.status_code
        data = json.loads(response.content)
        from urllib.parse import urlparse
        ingresses_url = urlparse(data['ingresses_url'])

        response = api_client.get(ingresses_url.path)
        assert 200 == response.status_code
        data = json.loads(response.content)
        ingress_url = urlparse(data['ingress_urls'][0])

        response = api_client.get(ingress_url.path)
        assert 200 == response.status_code
        data = json.loads(response.content)

        assert "test-ingress-1" == data['name']
        assert data['tls'] is True
        assert "visbert" in data["rules"][0]["host"]
        for entry in data['annotations']:
            if entry['key'] == 'foo':
                assert entry['value'] == 'bar'
            if entry['key'] == 'x':
                assert entry['value'] == 'y'
    finally:
        api.get_portal_net_v1().delete_namespaced_ingress("test-ingress-1", "default")
        api.get_portal_net_v1().delete_namespaced_ingress("test-ingress-2", "default")


@pytest.mark.skipif(minikube_unavailable(), reason="Minikube is unavailable")
def test_ingresshosts_list(api_client, admin_user_with_k8s):
    apply_k8s_yml(BASE_DIR + "fixtures/ingress1.yml")
    apply_k8s_yml(BASE_DIR + "fixtures/ingress2.yml")

    try:
        response = api_client.get(f'/api/{settings.API_VERSION}/ingresshosts/')
        assert 200 == response.status_code
        data = json.loads(response.content)
        for check_host in ["visbert.demo.datexis.com", "tasty.demo.datexis.com"]:
            assert check_host in data["hosts"]
    finally:
        api.get_portal_net_v1().delete_namespaced_ingress("test-ingress-1", "default")
        api.get_portal_net_v1().delete_namespaced_ingress("test-ingress-2", "default")

@pytest.mark.skipif(minikube_unavailable(), reason="Minikube is unavailable")
def test_empty_user_ingresses_list(api_client, admin_user_with_k8s):
    response = api_client.get(f'/api/{settings.API_VERSION}/namespaces/default/')
    assert 200 == response.status_code
    data = json.loads(response.content)
    from urllib.parse import urlparse
    ingresses_url = urlparse(data['ingresses_url'])

    response = api_client.get(ingresses_url.path)
    assert 200 == response.status_code
    data = json.loads(response.content)
    assert len(data['ingress_urls']) == 0

def test_broken_k8s_single_ingress(api_client, admin_user_with_k8s, mocker):
    mocker.patch('kubeportal.k8s.kubernetes_api.get_namespaced_ingress', side_effect=Exception())
    apply_k8s_yml(BASE_DIR + "fixtures/ingress1.yml")

    try:
        response = api_client.get(f'/api/{settings.API_VERSION}/namespaces/default/')
        assert 200 == response.status_code
        data = json.loads(response.content)
        from urllib.parse import urlparse
        ingresses_url = urlparse(data['ingresses_url'])

        response = api_client.get(ingresses_url.path)
        assert 200 == response.status_code
        data = json.loads(response.content)
        ingress_url = urlparse(data['ingress_urls'][0])

        response = api_client.get(ingress_url.path)
        assert response.status_code == 504
    finally:
        api.get_portal_net_v1().delete_namespaced_ingress("test-ingress-1", "default")
