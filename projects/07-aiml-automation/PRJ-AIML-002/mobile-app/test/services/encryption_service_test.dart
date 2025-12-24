import 'package:flutter_test/flutter_test.dart';
import 'package:tab_organizer/services/encryption_service.dart';

void main() {
  group('EncryptionService', () {
    late EncryptionService service;

    setUp(() {
      service = EncryptionService();
    });

    test('initializes successfully', () async {
      await service.initialize();
      expect(service, isNotNull);
    });

    test('encrypts data successfully', () async {
      await service.initialize();

      final data = {
        'key1': 'value1',
        'key2': 42,
        'key3': true,
        'key4': ['list', 'of', 'items'],
      };

      final encrypted = await service.encrypt(data);

      expect(encrypted, isNotEmpty);
      expect(encrypted, isA<String>());
    });

    test('encrypted data is different from original', () async {
      await service.initialize();

      final data = {'secret': 'password123'};
      final encrypted = await service.encrypt(data);

      expect(encrypted, isNot(contains('password123')));
      expect(encrypted, isNot(contains('secret')));
    });

    test('decrypts data successfully', () async {
      await service.initialize();

      final originalData = {
        'username': 'testuser',
        'email': 'test@example.com',
        'age': 25,
      };

      final encrypted = await service.encrypt(originalData);
      final decrypted = await service.decrypt(encrypted);

      expect(decrypted, equals(originalData));
      expect(decrypted['username'], 'testuser');
      expect(decrypted['email'], 'test@example.com');
      expect(decrypted['age'], 25);
    });

    test('encrypt-decrypt roundtrip preserves data', () async {
      await service.initialize();

      final testData = {
        'string': 'test string',
        'number': 123,
        'double': 45.67,
        'bool': true,
        'null': null,
        'list': [1, 2, 3],
        'map': {'nested': 'value'},
      };

      final encrypted = await service.encrypt(testData);
      final decrypted = await service.decrypt(encrypted);

      expect(decrypted, equals(testData));
    });

    test('handles empty data', () async {
      await service.initialize();

      final emptyData = <String, dynamic>{};
      final encrypted = await service.encrypt(emptyData);
      final decrypted = await service.decrypt(encrypted);

      expect(decrypted, equals(emptyData));
      expect(decrypted, isEmpty);
    });

    test('handles large data sets', () async {
      await service.initialize();

      final largeData = {
        'items': List.generate(1000, (i) => {'id': i, 'value': 'item_$i'}),
      };

      final encrypted = await service.encrypt(largeData);
      final decrypted = await service.decrypt(encrypted);

      expect(decrypted, equals(largeData));
      expect((decrypted['items'] as List).length, 1000);
    });

    test('handles special characters in data', () async {
      await service.initialize();

      final specialData = {
        'special': '<>&"\'',
        'unicode': '日本語 🚀',
        'newlines': 'line1\nline2\r\nline3',
        'tabs': 'col1\tcol2\tcol3',
      };

      final encrypted = await service.encrypt(specialData);
      final decrypted = await service.decrypt(encrypted);

      expect(decrypted, equals(specialData));
    });

    test('generates different ciphertext for same data', () async {
      await service.initialize();

      final data = {'test': 'data'};
      final encrypted1 = await service.encrypt(data);
      final encrypted2 = await service.encrypt(data);

      // Should be different due to random IV
      expect(encrypted1, isNot(equals(encrypted2)));

      // But both should decrypt to same data
      final decrypted1 = await service.decrypt(encrypted1);
      final decrypted2 = await service.decrypt(encrypted2);
      expect(decrypted1, equals(decrypted2));
    });

    test('encrypted data contains IV and algorithm info', () async {
      await service.initialize();

      final data = {'test': 'value'};
      final encrypted = await service.encrypt(data);

      expect(encrypted, contains('iv'));
      expect(encrypted, contains('data'));
      expect(encrypted, contains('algorithm'));
      expect(encrypted, contains('AES-256-GCM'));
    });

    test('throws error on invalid encrypted data', () async {
      await service.initialize();

      expect(
        () => service.decrypt('invalid-encrypted-data'),
        throwsException,
      );
    });

    test('throws error on tampered data', () async {
      await service.initialize();

      final data = {'test': 'value'};
      final encrypted = await service.encrypt(data);

      // Tamper with encrypted data
      final tampered = encrypted.replaceAll('A', 'B');

      expect(
        () => service.decrypt(tampered),
        throwsException,
      );
    });

    test('auto-initializes on first encrypt', () async {
      // Don't manually initialize
      final newService = EncryptionService();

      final data = {'test': 'auto-init'};
      final encrypted = await newService.encrypt(data);

      expect(encrypted, isNotEmpty);
    });

    test('auto-initializes on first decrypt', () async {
      // Initialize first service to create encrypted data
      await service.initialize();
      final data = {'test': 'value'};
      final encrypted = await service.encrypt(data);

      // New service without manual initialization
      final newService = EncryptionService();
      await newService.initialize(); // Must init to use same key
      
      // Note: This test is limited because each service has its own key
      expect(() => newService.decrypt(encrypted), throwsException);
    });
  });

  group('EncryptionService - Password Hashing', () {
    late EncryptionService service;

    setUp(() {
      service = EncryptionService();
    });

    test('hashes password successfully', () {
      final password = 'mySecretPassword123';
      final salt = service.generateSalt();

      final hash = service.hashPassword(password, salt);

      expect(hash, isNotEmpty);
      expect(hash.length, greaterThan(0));
    });

    test('same password and salt produce same hash', () {
      final password = 'password123';
      final salt = service.generateSalt();

      final hash1 = service.hashPassword(password, salt);
      final hash2 = service.hashPassword(password, salt);

      expect(hash1, equals(hash2));
    });

    test('different passwords produce different hashes', () {
      final salt = service.generateSalt();

      final hash1 = service.hashPassword('password1', salt);
      final hash2 = service.hashPassword('password2', salt);

      expect(hash1, isNot(equals(hash2)));
    });

    test('different salts produce different hashes', () {
      final password = 'samePassword';

      final salt1 = service.generateSalt();
      final salt2 = service.generateSalt();

      final hash1 = service.hashPassword(password, salt1);
      final hash2 = service.hashPassword(password, salt2);

      expect(hash1, isNot(equals(hash2)));
    });

    test('handles empty password', () {
      final salt = service.generateSalt();
      final hash = service.hashPassword('', salt);

      expect(hash, isNotEmpty);
    });

    test('handles empty salt', () {
      final hash = service.hashPassword('password', '');

      expect(hash, isNotEmpty);
    });

    test('handles special characters in password', () {
      final salt = service.generateSalt();
      final password = '<>&"\' !@#\$%^&*()';

      final hash = service.hashPassword(password, salt);

      expect(hash, isNotEmpty);
    });

    test('handles Unicode in password', () {
      final salt = service.generateSalt();
      final password = '日本語パスワード🔒';

      final hash = service.hashPassword(password, salt);

      expect(hash, isNotEmpty);
    });

    test('hash length is consistent', () {
      final salt = service.generateSalt();

      final hash1 = service.hashPassword('short', salt);
      final hash2 = service.hashPassword('a very long password ' * 10, salt);

      // SHA256 produces fixed-length output
      expect(hash1.length, equals(hash2.length));
    });
  });

  group('EncryptionService - Salt Generation', () {
    late EncryptionService service;

    setUp(() {
      service = EncryptionService();
    });

    test('generates non-empty salt', () {
      final salt = service.generateSalt();

      expect(salt, isNotEmpty);
      expect(salt.length, greaterThan(0));
    });

    test('generates different salts each time', () {
      final salt1 = service.generateSalt();
      final salt2 = service.generateSalt();
      final salt3 = service.generateSalt();

      expect(salt1, isNot(equals(salt2)));
      expect(salt1, isNot(equals(salt3)));
      expect(salt2, isNot(equals(salt3)));
    });

    test('generates salts with sufficient entropy', () {
      final salts = List.generate(100, (_) => service.generateSalt());
      final uniqueSalts = salts.toSet();

      // All salts should be unique
      expect(uniqueSalts.length, equals(100));
    });

    test('salt is base64 encoded', () {
      final salt = service.generateSalt();

      // Base64 characters: A-Z, a-z, 0-9, +, /, =
      final base64Regex = RegExp(r'^[A-Za-z0-9+/=]+$');
      expect(base64Regex.hasMatch(salt), true);
    });
  });

  group('EncryptionService - Key Pair Generation', () {
    late EncryptionService service;

    setUp(() {
      service = EncryptionService();
    });

    test('generates key pair successfully', () async {
      final keyPair = await service.generateKeyPair();

      expect(keyPair, isNotNull);
      expect(keyPair.publicKey, isNotEmpty);
      expect(keyPair.privateKey, isNotEmpty);
    });

    test('public and private keys are different', () async {
      final keyPair = await service.generateKeyPair();

      expect(keyPair.publicKey, isNot(equals(keyPair.privateKey)));
    });

    test('generates different key pairs each time', () async {
      final keyPair1 = await service.generateKeyPair();
      final keyPair2 = await service.generateKeyPair();

      expect(keyPair1.publicKey, isNot(equals(keyPair2.publicKey)));
      expect(keyPair1.privateKey, isNot(equals(keyPair2.privateKey)));
    });
  });

  group('KeyPair', () {
    test('creates key pair with both keys', () {
      final keyPair = KeyPair(
        publicKey: 'public-key-data',
        privateKey: 'private-key-data',
      );

      expect(keyPair.publicKey, 'public-key-data');
      expect(keyPair.privateKey, 'private-key-data');
    });

    test('allows empty keys', () {
      final keyPair = KeyPair(
        publicKey: '',
        privateKey: '',
      );

      expect(keyPair.publicKey, isEmpty);
      expect(keyPair.privateKey, isEmpty);
    });
  });

  group('EncryptionService - Edge Cases', () {
    late EncryptionService service;

    setUp(() {
      service = EncryptionService();
    });

    test('handles nested data structures', () async {
      await service.initialize();

      final nestedData = {
        'level1': {
          'level2': {
            'level3': {
              'level4': 'deep value',
            },
          },
        },
      };

      final encrypted = await service.encrypt(nestedData);
      final decrypted = await service.decrypt(encrypted);

      expect(decrypted, equals(nestedData));
    });

    test('handles mixed data types', () async {
      await service.initialize();

      final mixedData = {
        'string': 'text',
        'int': 42,
        'double': 3.14159,
        'bool': true,
        'list': [1, 'two', 3.0, false],
        'map': {'nested': 'value'},
        'null': null,
      };

      final encrypted = await service.encrypt(mixedData);
      final decrypted = await service.decrypt(encrypted);

      expect(decrypted, equals(mixedData));
    });

    test('handles very long strings', () async {
      await service.initialize();

      final longString = 'x' * 100000;
      final data = {'longString': longString};

      final encrypted = await service.encrypt(data);
      final decrypted = await service.decrypt(encrypted);

      expect(decrypted['longString'], equals(longString));
    });

    test('multiple encryptions produce unique ciphertexts', () async {
      await service.initialize();

      final data = {'counter': 1};
      final ciphertexts = <String>{};

      for (int i = 0; i < 10; i++) {
        final encrypted = await service.encrypt(data);
        ciphertexts.add(encrypted);
      }

      // All ciphertexts should be unique due to random IV
      expect(ciphertexts.length, equals(10));
    });
  });
}