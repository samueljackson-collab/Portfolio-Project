import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:hive/hive.dart';
import 'tab.dart';

part 'tab_group.freezed.dart';
part 'tab_group.g.dart';

@freezed
@HiveType(typeId: 2)
class TabGroup with _$TabGroup {
  const factory TabGroup({
    @HiveField(0) required String id,
    @HiveField(1) required String name,
    @HiveField(2) required TabCategory category,
    @HiveField(3) required List<String> tabIds,
    @HiveField(4) required DateTime createdAt,
    @HiveField(5) DateTime? updatedAt,
    @HiveField(6) int? colorValue,
    @HiveField(7) @Default(false) bool isPinned,
    @HiveField(8) @Default(false) bool isCollapsed,
    @HiveField(9) Map<String, dynamic>? metadata,
  }) = _TabGroup;

  factory TabGroup.fromJson(Map<String, dynamic> json) =>
      _$TabGroupFromJson(json);
}

extension TabGroupExtension on TabGroup {
  int get color => colorValue ?? category.colorValue;

  int get tabCount => tabIds.length;

  bool get isEmpty => tabIds.isEmpty;

  TabGroup addTab(String tabId) {
    return copyWith(
      tabIds: [...tabIds, tabId],
      updatedAt: DateTime.now(),
    );
  }

  TabGroup removeTab(String tabId) {
    return copyWith(
      tabIds: tabIds.where((id) => id != tabId).toList(),
      updatedAt: DateTime.now(),
    );
  }

  TabGroup rename(String newName) {
    return copyWith(
      name: newName,
      updatedAt: DateTime.now(),
    );
  }
}
