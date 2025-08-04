#!/usr/bin/env python3
"""
Финальный тест Organizations Directory API
"""
import requests
import json

BASE_URL = "http://31.130.149.12:8000"
API_KEY = "my_super_secret_api_key_2024"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def test_all():
    print("ТЕСТИРОВАНИЕ Organizations Directory API")
    print("")
    
    results = {}
    
    # 1. Health Check
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        results["Health Check"] = resp.status_code == 200
        print(f"Health Check: {'OK' if results['Health Check'] else 'FAIL'} ({resp.status_code})")
    except Exception as e:
        results["Health Check"] = False
        print(f"Health Check: FAIL ({e})")
    
    # 2. Аутентификация
    auth_tests = []
    
    # Без API ключа
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/organizations/", timeout=5)
        auth_tests.append(resp.status_code == 401)
        print(f"Без API ключа: {'OK' if resp.status_code == 401 else 'FAIL'} ({resp.status_code})")
    except Exception as e:
        auth_tests.append(False)
        print(f"Без API ключа: FAIL ({e})")
    
    # С неверным ключом
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/organizations/", 
                           headers={"Authorization": "Bearer wrong"}, timeout=5)
        auth_tests.append(resp.status_code == 401)
        print(f"Неверный ключ: {'OK' if resp.status_code == 401 else 'FAIL'} ({resp.status_code})")
    except Exception as e:
        auth_tests.append(False)
        print(f"Неверный ключ: FAIL ({e})")
    
    # С правильным ключом
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/organizations/", headers=HEADERS, timeout=5)
        auth_tests.append(resp.status_code == 200)
        print(f"Правильный ключ: {'OK' if resp.status_code == 200 else 'FAIL'} ({resp.status_code})")
    except Exception as e:
        auth_tests.append(False)
        print(f"Правильный ключ: FAIL ({e})")
    
    results["Аутентификация"] = all(auth_tests)
    
    # 3. Organizations API
    org_tests = []
    try:
        # GET список
        resp = requests.get(f"{BASE_URL}/api/v1/organizations/", headers=HEADERS, timeout=5)
        org_tests.append(resp.status_code == 200)
        print(f"GET organizations: {'OK' if resp.status_code == 200 else 'FAIL'} ({resp.status_code})")
        
        # GET по ID
        resp = requests.get(f"{BASE_URL}/api/v1/organizations/1", headers=HEADERS, timeout=5)
        org_tests.append(resp.status_code == 200)
        print(f"GET organization/1: {'OK' if resp.status_code == 200 else 'FAIL'} ({resp.status_code})")
        
        # POST создание
        data = {
            "name": "Test Org",
            "building_id": 1,
            "phone_numbers": ["8-999-888-77-66"],
            "activity_ids": [1]
        }
        resp = requests.post(f"{BASE_URL}/api/v1/organizations/", 
                           json=data, headers=HEADERS, timeout=5)
        org_tests.append(resp.status_code == 200)
        print(f"POST organization: {'OK' if resp.status_code == 200 else 'FAIL'} ({resp.status_code})")
        
    except Exception as e:
        org_tests.append(False)
        print(f"Organizations API: FAIL ({e})")
    
    results["Organizations API"] = all(org_tests)
    
    # 4. Buildings API
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/buildings/", headers=HEADERS, timeout=5)
        results["Buildings API"] = resp.status_code == 200
        print(f"Buildings API: {'OK' if results['Buildings API'] else 'FAIL'} ({resp.status_code})")
    except Exception as e:
        results["Buildings API"] = False
        print(f"Buildings API: FAIL ({e})")
    
    # 5. Activities API
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/activities/", headers=HEADERS, timeout=5)
        results["Activities API"] = resp.status_code == 200
        print(f"Activities API: {'OK' if results['Activities API'] else 'FAIL'} ({resp.status_code})")
    except Exception as e:
        results["Activities API"] = False
        print(f"Activities API: FAIL ({e})")
    
    # 6. Обработка ошибок
    error_tests = []
    
    # 404 для несуществующего endpoint
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/nonexistent", timeout=5)
        error_tests.append(resp.status_code == 404)
        print(f"404 endpoint: {'OK' if resp.status_code == 404 else 'FAIL'} ({resp.status_code})")
    except Exception as e:
        error_tests.append(False)
        print(f"404 endpoint: FAIL ({e})")
    
    # 404 для несуществующей организации
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/organizations/99999", headers=HEADERS, timeout=5)
        error_tests.append(resp.status_code == 404)
        print(f"404 organization: {'OK' if resp.status_code == 404 else 'FAIL'} ({resp.status_code})")
    except Exception as e:
        error_tests.append(False)
        print(f"404 organization: FAIL ({e})")
    
    # 422 для невалидных данных
    try:
        invalid_data = {"name": "", "building_id": 99999, "phone_numbers": [], "activity_ids": []}
        resp = requests.post(f"{BASE_URL}/api/v1/organizations/", 
                           json=invalid_data, headers=HEADERS, timeout=5)
        error_tests.append(resp.status_code == 422)
        print(f"422 invalid: {'OK' if resp.status_code == 422 else 'FAIL'} ({resp.status_code})")
    except Exception as e:
        error_tests.append(False)
        print(f"422 invalid: FAIL ({e})")
    
    results["Обработка ошибок"] = all(error_tests)
    
    # 7. Документация
    docs_tests = []
    try:
        resp = requests.get(f"{BASE_URL}/docs", timeout=5)
        docs_tests.append(resp.status_code == 200)
        resp = requests.get(f"{BASE_URL}/redoc", timeout=5)
        docs_tests.append(resp.status_code == 200)
        results["Документация"] = all(docs_tests)
        print(f"Документация: {'OK' if results['Документация'] else 'FAIL'}")
    except Exception as e:
        results["Документация"] = False
        print(f"Документация: FAIL ({e})")
    
    # Итоги
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "OK" if result else "FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print("=" * 60)
    if passed == total:
        print("ВСЕ ТЕСТЫ ПРОШЛИ")
        print(f"Пройдено: {passed}/{total}")
        return 0
    else:
        print("НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print(f"Пройдено: {passed}/{total}")
        print(f"Провалено: {total - passed}/{total}")
        return 1

if __name__ == "__main__":
    exit(test_all())