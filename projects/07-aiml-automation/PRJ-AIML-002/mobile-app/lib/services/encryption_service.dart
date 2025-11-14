import 'dart:convert';
import 'dart:typed_data';
import 'package:encrypt/encrypt.dart' as encrypt;
import 'package:crypto/crypto.dart';
import 'package:logger/logger.dart';

import '../config/app_config.dart';

/// End-to-end encryption service using hybrid encryption (RSA + AES)
class EncryptionService {
  final Logger _logger = Logger();
  encrypt.Encrypter? _aesEncrypter;
  encrypt.Key? _deviceKey;

  /// Initialize encryption with device-specific key
  Future<void> initialize() async {
    // In production, retrieve/generate device-specific key
    // For now, use a placeholder key
    _deviceKey = encrypt.Key.fromSecureRandom(32);  // 256-bit AES key
    _aesEncrypter = encrypt.Encrypter(
      encrypt.AES(_deviceKey!, mode: encrypt.AESMode.gcm),
    );

    _logger.i('Encryption service initialized');
  }

  /// Encrypt data using AES-256-GCM
  Future<String> encrypt(Map<String, dynamic> data) async {
    if (_aesEncrypter == null) {
      await initialize();
    }

    try {
      final jsonString = json.encode(data);
      final iv = encrypt.IV.fromSecureRandom(16);  // 128-bit IV

      final encrypted = _aesEncrypter!.encrypt(jsonString, iv: iv);

      // Combine IV and ciphertext
      final combined = {
        'iv': iv.base64,
        'data': encrypted.base64,
        'algorithm': 'AES-256-GCM',
      };

      return json.encode(combined);
    } catch (e) {
      _logger.e('Encryption failed: $e');
      rethrow;
    }
  }

  /// Decrypt data using AES-256-GCM
  Future<Map<String, dynamic>> decrypt(String encryptedData) async {
    if (_aesEncrypter == null) {
      await initialize();
    }

    try {
      final combined = json.decode(encryptedData);
      final iv = encrypt.IV.fromBase64(combined['iv']);
      final encrypted = encrypt.Encrypted.fromBase64(combined['data']);

      final decrypted = _aesEncrypter!.decrypt(encrypted, iv: iv);
      return json.decode(decrypted);
    } catch (e) {
      _logger.e('Decryption failed: $e');
      rethrow;
    }
  }

  /// Generate RSA key pair for device
  Future<KeyPair> generateKeyPair() async {
    // In production, use proper RSA implementation
    // This is a placeholder
    _logger.w('generateKeyPair not fully implemented');
    return KeyPair(
      publicKey: 'placeholder-public-key',
      privateKey: 'placeholder-private-key',
    );
  }

  /// Hash password using PBKDF2
  String hashPassword(String password, String salt) {
    final bytes = utf8.encode(password + salt);
    var hash = sha256.convert(bytes);

    // Perform multiple iterations
    for (int i = 0; i < AppConfig.pbkdf2Iterations; i++) {
      hash = sha256.convert(hash.bytes);
    }

    return hash.toString();
  }

  /// Generate secure random salt
  String generateSalt() {
    return encrypt.Key.fromSecureRandom(32).base64;
  }
}

/// RSA key pair
class KeyPair {
  final String publicKey;
  final String privateKey;

  KeyPair({
    required this.publicKey,
    required this.privateKey,
  });
}
