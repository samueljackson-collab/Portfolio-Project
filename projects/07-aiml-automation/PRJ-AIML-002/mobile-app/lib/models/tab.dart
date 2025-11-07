import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:hive/hive.dart';

part 'tab.freezed.dart';
part 'tab.g.dart';

@freezed
@HiveType(typeId: 0)
class Tab with _$Tab {
  const factory Tab({
    @HiveField(0) required String id,
    @HiveField(1) required String url,
    @HiveField(2) required String title,
    @HiveField(3) String? description,
    @HiveField(4) String? faviconUrl,
    @HiveField(5) required DateTime createdAt,
    @HiveField(6) DateTime? lastAccessed,
    @HiveField(7) @Default(1) int visitCount,
    @HiveField(8) String? groupId,
    @HiveField(9) TabCategory? category,
    @HiveField(10) @Default(false) bool isHibernated,
    @HiveField(11) Map<String, dynamic>? metadata,
  }) = _Tab;

  factory Tab.fromJson(Map<String, dynamic> json) => _$TabFromJson(json);
}

@HiveType(typeId: 1)
enum TabCategory {
  @HiveField(0)
  work,
  @HiveField(1)
  research,
  @HiveField(2)
  shopping,
  @HiveField(3)
  socialMedia,
  @HiveField(4)
  entertainment,
  @HiveField(5)
  news,
  @HiveField(6)
  finance,
  @HiveField(7)
  education,
  @HiveField(8)
  other,
}

extension TabCategoryExtension on TabCategory {
  String get displayName {
    switch (this) {
      case TabCategory.work:
        return 'Work';
      case TabCategory.research:
        return 'Research';
      case TabCategory.shopping:
        return 'Shopping';
      case TabCategory.socialMedia:
        return 'Social Media';
      case TabCategory.entertainment:
        return 'Entertainment';
      case TabCategory.news:
        return 'News';
      case TabCategory.finance:
        return 'Finance';
      case TabCategory.education:
        return 'Education';
      case TabCategory.other:
        return 'Other';
    }
  }

  int get colorValue {
    switch (this) {
      case TabCategory.work:
        return 0xFF2196F3;
      case TabCategory.research:
        return 0xFF9C27B0;
      case TabCategory.shopping:
        return 0xFFFF9800;
      case TabCategory.socialMedia:
        return 0xFFE91E63;
      case TabCategory.entertainment:
        return 0xFFF44336;
      case TabCategory.news:
        return 0xFF4CAF50;
      case TabCategory.finance:
        return 0xFF00BCD4;
      case TabCategory.education:
        return 0xFF3F51B5;
      case TabCategory.other:
        return 0xFF9E9E9E;
    }
  }
}

extension TabExtension on Tab {
  String get domain {
    try {
      final uri = Uri.parse(url);
      return uri.host;
    } catch (e) {
      return '';
    }
  }

  String get searchableText {
    final parts = [
      title,
      url,
      description ?? '',
    ];
    return parts.join(' ').toLowerCase();
  }
}
