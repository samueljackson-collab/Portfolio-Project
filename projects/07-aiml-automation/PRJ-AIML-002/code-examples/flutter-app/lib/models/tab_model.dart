import 'package:json_annotation/json_annotation.dart';
import 'package:hive/hive.dart';

part 'tab_model.g.dart';

@HiveType(typeId: 0)
@JsonSerializable()
class TabModel {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String title;

  @HiveField(2)
  final String url;

  @HiveField(3)
  final String? faviconUrl;

  @HiveField(4)
  final String category;

  @HiveField(5)
  final double confidenceScore;

  @HiveField(6)
  final DateTime createdAt;

  @HiveField(7)
  final DateTime lastAccessed;

  @HiveField(8)
  final String? groupId;

  @HiveField(9)
  final String browser; // 'chrome', 'firefox', 'edge'

  @HiveField(10)
  final int tabIndex;

  @HiveField(11)
  final bool isPinned;

  @HiveField(12)
  final bool isActive;

  @HiveField(13)
  final String? domain;

  @HiveField(14)
  final Map<String, dynamic>? metadata;

  TabModel({
    required this.id,
    required this.title,
    required this.url,
    this.faviconUrl,
    required this.category,
    required this.confidenceScore,
    required this.createdAt,
    required this.lastAccessed,
    this.groupId,
    required this.browser,
    required this.tabIndex,
    this.isPinned = false,
    this.isActive = false,
    this.domain,
    this.metadata,
  });

  factory TabModel.fromJson(Map<String, dynamic> json) =>
      _$TabModelFromJson(json);

  Map<String, dynamic> toJson() => _$TabModelToJson(this);

  TabModel copyWith({
    String? id,
    String? title,
    String? url,
    String? faviconUrl,
    String? category,
    double? confidenceScore,
    DateTime? createdAt,
    DateTime? lastAccessed,
    String? groupId,
    String? browser,
    int? tabIndex,
    bool? isPinned,
    bool? isActive,
    String? domain,
    Map<String, dynamic>? metadata,
  }) {
    return TabModel(
      id: id ?? this.id,
      title: title ?? this.title,
      url: url ?? this.url,
      faviconUrl: faviconUrl ?? this.faviconUrl,
      category: category ?? this.category,
      confidenceScore: confidenceScore ?? this.confidenceScore,
      createdAt: createdAt ?? this.createdAt,
      lastAccessed: lastAccessed ?? this.lastAccessed,
      groupId: groupId ?? this.groupId,
      browser: browser ?? this.browser,
      tabIndex: tabIndex ?? this.tabIndex,
      isPinned: isPinned ?? this.isPinned,
      isActive: isActive ?? this.isActive,
      domain: domain ?? this.domain,
      metadata: metadata ?? this.metadata,
    );
  }

  @override
  String toString() {
    return 'TabModel(id: $id, title: $title, url: $url, category: $category)';
  }
}

@HiveType(typeId: 1)
@JsonSerializable()
class TabGroup {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String name;

  @HiveField(2)
  final String category;

  @HiveField(3)
  final List<String> tabIds;

  @HiveField(4)
  final String colorHex;

  @HiveField(5)
  final DateTime createdAt;

  @HiveField(6)
  final DateTime updatedAt;

  @HiveField(7)
  final bool isCollapsed;

  @HiveField(8)
  final int sortOrder;

  @HiveField(9)
  final Map<String, dynamic>? metadata;

  TabGroup({
    required this.id,
    required this.name,
    required this.category,
    required this.tabIds,
    required this.colorHex,
    required this.createdAt,
    required this.updatedAt,
    this.isCollapsed = false,
    this.sortOrder = 0,
    this.metadata,
  });

  factory TabGroup.fromJson(Map<String, dynamic> json) =>
      _$TabGroupFromJson(json);

  Map<String, dynamic> toJson() => _$TabGroupToJson(this);

  TabGroup copyWith({
    String? id,
    String? name,
    String? category,
    List<String>? tabIds,
    String? colorHex,
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? isCollapsed,
    int? sortOrder,
    Map<String, dynamic>? metadata,
  }) {
    return TabGroup(
      id: id ?? this.id,
      name: name ?? this.name,
      category: category ?? this.category,
      tabIds: tabIds ?? this.tabIds,
      colorHex: colorHex ?? this.colorHex,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      isCollapsed: isCollapsed ?? this.isCollapsed,
      sortOrder: sortOrder ?? this.sortOrder,
      metadata: metadata ?? this.metadata,
    );
  }

  int get tabCount => tabIds.length;

  @override
  String toString() {
    return 'TabGroup(id: $id, name: $name, category: $category, tabCount: $tabCount)';
  }
}
