import 'dart:io';
import 'dart:math';
import 'package:flutter/services.dart';
import 'package:tflite_flutter/tflite_flutter.dart';
import 'package:logger/logger.dart';

import '../config/app_config.dart';
import '../models/tab.dart';

/// AI-powered tab classification service using TensorFlow Lite
class TabClassifier {
  static final TabClassifier _instance = TabClassifier._internal();
  static TabClassifier get instance => _instance;

  Interpreter? _interpreter;
  final Logger _logger = Logger();
  bool _isInitialized = false;

  TabClassifier._internal();

  /// Initialize the ML model
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      _logger.i('Initializing TensorFlow Lite model...');

      // Load model from assets
      final interpreterOptions = InterpreterOptions();

      // Enable GPU acceleration if available
      if (AppConfig.enableGpuAcceleration) {
        if (Platform.isAndroid) {
          interpreterOptions.addDelegate(GpuDelegateV2());
        } else if (Platform.isIOS) {
          interpreterOptions.addDelegate(GpuDelegate());
        }
      }

      _interpreter = await Interpreter.fromAsset(
        'assets/models/tab_classifier.tflite',
        options: interpreterOptions,
      );

      _logger.i('Model loaded successfully');
      _logger.i('Input shape: ${_interpreter!.getInputTensor(0).shape}');
      _logger.i('Output shape: ${_interpreter!.getOutputTensor(0).shape}');

      _isInitialized = true;
    } catch (e) {
      _logger.e('Failed to initialize model: $e');
      rethrow;
    }
  }

  /// Classify a single tab
  Future<ClassificationResult> classifyTab(Tab tab) async {
    if (!_isInitialized) {
      await initialize();
    }

    try {
      final startTime = DateTime.now();

      // Extract features from tab
      final features = _extractFeatures(tab);

      // Prepare input tensor
      final input = _prepareInput(features);

      // Prepare output tensor
      final output = List.filled(9, 0.0).reshape([1, 9]);

      // Run inference
      _interpreter!.run(input, output);

      // Parse results
      final probabilities = output[0] as List<double>;
      final maxIndex = _getMaxIndex(probabilities);
      final confidence = probabilities[maxIndex];

      final inferenceTime = DateTime.now().difference(startTime);
      _logger.d('Inference completed in ${inferenceTime.inMilliseconds}ms');

      // Return result
      return ClassificationResult(
        category: confidence >= AppConfig.classificationThreshold
            ? TabCategory.values[maxIndex]
            : TabCategory.other,
        confidence: confidence,
        probabilities: Map.fromIterables(
          TabCategory.values,
          probabilities,
        ),
        inferenceTimeMs: inferenceTime.inMilliseconds,
      );
    } catch (e) {
      _logger.e('Classification failed: $e');
      return ClassificationResult.fallback();
    }
  }

  /// Classify multiple tabs in batch
  Future<List<ClassificationResult>> classifyBatch(List<Tab> tabs) async {
    final results = <ClassificationResult>[];

    // Process in batches for better performance
    for (var i = 0; i < tabs.length; i += AppConfig.maxBatchSize) {
      final end = min(i + AppConfig.maxBatchSize, tabs.length);
      final batch = tabs.sublist(i, end);

      final batchResults = await Future.wait(
        batch.map((tab) => classifyTab(tab)),
      );

      results.addAll(batchResults);
    }

    return results;
  }

  /// Extract features from tab for classification
  Map<String, dynamic> _extractFeatures(Tab tab) {
    // URL features
    final domain = tab.domain;
    final path = Uri.tryParse(tab.url)?.path ?? '';
    final tld = domain.split('.').last;

    // Text features
    final title = tab.title.toLowerCase();
    final description = (tab.description ?? '').toLowerCase();
    final combinedText = '$title $description';

    // Behavioral features
    final visitFrequency = tab.visitCount / max(1,
        DateTime.now().difference(tab.createdAt).inDays);
    final hourOfDay = tab.lastAccessed?.hour ?? DateTime.now().hour;

    return {
      'domain': domain,
      'path': path,
      'tld': tld,
      'title': title,
      'description': description,
      'combined_text': combinedText,
      'visit_frequency': visitFrequency,
      'hour_of_day': hourOfDay,
      'visit_count': tab.visitCount,
    };
  }

  /// Prepare input tensor from features
  List<List<double>> _prepareInput(Map<String, dynamic> features) {
    // Simplified tokenization (in production, use proper tokenizer)
    final text = features['combined_text'] as String;
    final tokens = _tokenize(text);

    // Pad or truncate to max length
    final paddedTokens = _padSequence(tokens, AppConfig.maxTokens);

    return [paddedTokens];
  }

  /// Simple tokenization (replace with proper BERT tokenizer in production)
  List<double> _tokenize(String text) {
    final words = text.split(RegExp(r'\s+'));
    // Convert words to token IDs (simplified - use vocab in production)
    return words.take(AppConfig.maxTokens).map((word) {
      return word.hashCode.abs() % 30000;  // Simplified hashing
    }).map((e) => e.toDouble()).toList();
  }

  /// Pad or truncate sequence to target length
  List<double> _padSequence(List<double> sequence, int length) {
    if (sequence.length >= length) {
      return sequence.sublist(0, length);
    } else {
      return [...sequence, ...List.filled(length - sequence.length, 0.0)];
    }
  }

  /// Get index of maximum value in list
  int _getMaxIndex(List<double> values) {
    double maxValue = values[0];
    int maxIndex = 0;

    for (int i = 1; i < values.length; i++) {
      if (values[i] > maxValue) {
        maxValue = values[i];
        maxIndex = i;
      }
    }

    return maxIndex;
  }

  /// Clean up resources
  void dispose() {
    _interpreter?.close();
    _isInitialized = false;
  }
}

/// Classification result
class ClassificationResult {
  final TabCategory category;
  final double confidence;
  final Map<TabCategory, double> probabilities;
  final int inferenceTimeMs;

  ClassificationResult({
    required this.category,
    required this.confidence,
    required this.probabilities,
    required this.inferenceTimeMs,
  });

  /// Fallback result for errors
  factory ClassificationResult.fallback() {
    return ClassificationResult(
      category: TabCategory.other,
      confidence: 0.0,
      probabilities: {},
      inferenceTimeMs: 0,
    );
  }

  @override
  String toString() {
    return 'ClassificationResult(category: ${category.displayName}, '
        'confidence: ${(confidence * 100).toStringAsFixed(1)}%, '
        'time: ${inferenceTimeMs}ms)';
  }
}
