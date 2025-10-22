import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import pytest
import main
from main import load_users

def test_load_users_returns_empty_list_when_file_does_not_exist(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert result == []
    assert not users_file.exists()

def test_load_users_returns_users_from_valid_json_file(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [
        {"user_id": "1", "name": "alice", "password": "hash1"},
        {"user_id": "2", "name": "bob", "password": "hash2"}
    ]
    with open(users_file, 'w') as f:
        json.dump(users_data, f)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert result == users_data
    assert len(result) == 2
    assert result[0]['name'] == 'alice'
    assert result[1]['name'] == 'bob'

def test_load_users_returns_empty_list_for_corrupted_json(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_file.write_text("not valid json at all")
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert result == []

def test_load_users_returns_empty_list_for_empty_json_file(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_file.write_text("")
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert result == []

def test_load_users_handles_json_with_extra_whitespace(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [{"user_id": "1", "name": "charlie"}]
    with open(users_file, 'w') as f:
        json.dump(users_data, f, indent=4)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert result == users_data

def test_load_users_returns_empty_array_when_json_is_empty_array(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    with open(users_file, 'w') as f:
        json.dump([], f)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert result == []
    assert isinstance(result, list)

def test_load_users_handles_json_with_nested_profiles(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [{
        "user_id": "1",
        "name": "dave",
        "password": "hash",
        "profiles": [
            {"profile_id": "p1", "profile_name": "work", "currency": "USD"},
            {"profile_id": "p2", "profile_name": "personal", "currency": "EUR"}
        ]
    }]
    with open(users_file, 'w') as f:
        json.dump(users_data, f)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert len(result) == 1
    assert len(result[0]['profiles']) == 2
    assert result[0]['profiles'][0]['profile_name'] == 'work'
    assert result[0]['profiles'][1]['currency'] == 'EUR'

def test_load_users_handles_incomplete_json_object(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_file.write_text('{"user_id": "1", "name": "eve"')  # Missing closing brace
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert result == []

def test_load_users_handles_json_with_unicode_characters(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [{"user_id": "1", "name": "François", "password": "hash"}]
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert result == users_data
    assert result[0]['name'] == "François"

# New test cases

def test_load_users_handles_single_user(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [{"user_id": "1", "name": "single_user", "password": "hash"}]
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert len(result) == 1
    assert result[0]['name'] == 'single_user'

def test_load_users_handles_large_number_of_users(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [{"user_id": str(i), "name": f"user{i}", "password": f"hash{i}"} for i in range(100)]
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert len(result) == 100
    assert result[0]['name'] == 'user0'
    assert result[99]['name'] == 'user99'

def test_load_users_handles_users_with_missing_fields(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [
        {"user_id": "1", "name": "alice"},  # missing password
        {"user_id": "2", "password": "hash"}  # missing name
    ]
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert len(result) == 2
    assert 'password' not in result[0]
    assert 'name' not in result[1]

def test_load_users_handles_users_with_extra_fields(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [{"user_id": "1", "name": "alice", "password": "hash", "email": "alice@example.com", "age": 30}]
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert len(result) == 1
    assert result[0]['email'] == 'alice@example.com'
    assert result[0]['age'] == 30

def test_load_users_handles_json_with_null_values(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [{"user_id": "1", "name": None, "password": "hash"}]
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert len(result) == 1
    assert result[0]['name'] is None

def test_load_users_handles_json_with_boolean_values(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [{"user_id": "1", "name": "bob", "password": "hash", "is_active": True, "is_admin": False}]
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert len(result) == 1
    assert result[0]['is_active'] is True
    assert result[0]['is_admin'] is False

def test_load_users_handles_json_with_numeric_values(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [{"user_id": "1", "name": "charlie", "password": "hash", "age": 25, "balance": 1000.50}]
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert len(result) == 1
    assert result[0]['age'] == 25
    assert result[0]['balance'] == 1000.50

def test_load_users_handles_deeply_nested_profiles(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [{
        "user_id": "1",
        "name": "dave",
        "password": "hash",
        "profiles": [
            {
                "profile_id": "p1",
                "profile_name": "work",
                "currency": "USD",
                "settings": {
                    "notifications": True,
                    "theme": "dark"
                }
            }
        ]
    }]
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert len(result) == 1
    assert result[0]['profiles'][0]['settings']['notifications'] is True
    assert result[0]['profiles'][0]['settings']['theme'] == 'dark'

def test_load_users_handles_special_characters_in_names(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [
        {"user_id": "1", "name": "user@#$%", "password": "hash"},
        {"user_id": "2", "name": "user with spaces", "password": "hash"},
        {"user_id": "3", "name": "user\twith\ttabs", "password": "hash"}
    ]
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert len(result) == 3
    assert result[0]['name'] == "user@#$%"
    assert result[1]['name'] == "user with spaces"
    assert result[2]['name'] == "user\twith\ttabs"

def test_load_users_handles_empty_strings(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [{"user_id": "", "name": "", "password": ""}]
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert len(result) == 1
    assert result[0]['user_id'] == ""
    assert result[0]['name'] == ""
    assert result[0]['password'] == ""

def test_load_users_preserves_data_types(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_data = [{
        "user_id": "1",
        "name": "eve",
        "tags": ["admin", "user"],
        "metadata": {"created": "2025-01-01", "count": 42}
    }]
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f)
    
    monkeypatch.setattr(main, 'USERS_FILE', str(users_file))
    
    result = load_users()
    
    assert len(result) == 1
    assert isinstance(result[0]['tags'], list)
    assert isinstance(result[0]['metadata'], dict)
    assert result[0]['tags'] == ["admin", "user"]
    assert result[0]['metadata']['count'] == 42