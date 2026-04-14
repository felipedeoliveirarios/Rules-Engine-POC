from typing import NamedTuple
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field

from app.models import Rule


class FieldValueType(Enum):
    ABSOLUTE = "absolute"
    ABSOLUTE_MODIFIER = "absolute_modifier"
    PERCENT_MODIFIER = "percent_modifier"
    MULTIPLIER_MODIFIER = "multiplier_modifier"


class FieldValue(NamedTuple):
    numeric_value: Decimal = Decimal(0)
    type: FieldValueType = FieldValueType.ABSOLUTE


@dataclass
class FieldData:
    done: bool = False
    modifiers: list[FieldValue] = field(default_factory=list)
    base_value: FieldValue | None = None


@dataclass
class RuleValues:
    monthly_fee: FieldData = field(default_factory=FieldData)
    max_discount: FieldData = field(default_factory=FieldData)
    cashback: FieldData = field(default_factory=FieldData)
    trial_days: FieldData = field(default_factory=FieldData)
    points_modifier: FieldData = field(default_factory=FieldData)
    
    def all_done(self) -> bool:
        return all([
            self.monthly_fee.done,
            self.max_discount.done,
            self.cashback.done,
            self.trial_days.done,
            self.points_modifier.done
        ])


@dataclass
class ConsolidatedRule:
    monthly_fee: Decimal | None = None
    max_discount: Decimal | None = None
    cashback: Decimal | None = None
    trial_days: Decimal | None = None
    points_modifier: Decimal | None = None


class RuleConsolidator:
    def consolidate(self, rules: list[Rule]) -> ConsolidatedRule:
        rule_values = self._extract_rule_values(rules)
        
        return ConsolidatedRule(
            monthly_fee=self._consolidate_field(rule_values.monthly_fee),
            max_discount=self._consolidate_field(rule_values.max_discount),
            cashback=self._consolidate_field(rule_values.cashback),
            trial_days=self._consolidate_field(rule_values.trial_days),
            points_modifier=self._consolidate_field(rule_values.points_modifier),
        )

    def _parse_rule_value(self, rule_value_str: str) -> FieldValue:
        if rule_value_str.startswith('='):
            return FieldValue(Decimal(rule_value_str[1:]), FieldValueType.ABSOLUTE)
        
        if rule_value_str.startswith('x'):
            return FieldValue(Decimal(rule_value_str[1:]), FieldValueType.MULTIPLIER_MODIFIER)
        
        if rule_value_str.endswith('%'):
            return FieldValue(Decimal(rule_value_str[:-1]), FieldValueType.PERCENT_MODIFIER)
        
        # +N ou -N → modificador absoluto
        return FieldValue(Decimal(rule_value_str), FieldValueType.ABSOLUTE_MODIFIER)

    def _process_field(self, field_data: FieldData, value_str: str | None) -> None:
        if field_data.done or not value_str:
            return
        
        rule_value = self._parse_rule_value(value_str)
        
        if rule_value.type == FieldValueType.ABSOLUTE:
            field_data.base_value = rule_value
            field_data.done = True
        else:
            field_data.modifiers.append(rule_value)

    def _extract_rule_values(self, rules: list[Rule]) -> RuleValues:
        rule_values = RuleValues()

        for rule in rules:
            self._process_field(rule_values.monthly_fee, rule.monthly_fee)
            self._process_field(rule_values.max_discount, rule.max_discount)
            self._process_field(rule_values.cashback, rule.cashback)
            self._process_field(rule_values.trial_days, rule.trial_days)
            self._process_field(rule_values.points_modifier, rule.points_modifier)

            if rule_values.all_done():
                break
        
        return rule_values

    def _consolidate_field(self, field_data: FieldData) -> Decimal | None:
        if field_data.base_value is None:
            return None
            
        absolute_modifier = Decimal(0)
        percent_modifier = Decimal(100)
        multiplier_modifier: Decimal | None = None
        
        for modifier in field_data.modifiers:
            if modifier.type == FieldValueType.ABSOLUTE_MODIFIER:
                absolute_modifier += modifier.numeric_value
            elif modifier.type == FieldValueType.PERCENT_MODIFIER:
                percent_modifier += modifier.numeric_value
            else:
                if multiplier_modifier is None:
                    multiplier_modifier = modifier.numeric_value
                else:
                    multiplier_modifier *= modifier.numeric_value
        
        final_value = field_data.base_value.numeric_value
        final_value += absolute_modifier
        
        if multiplier_modifier is not None:
            final_value *= multiplier_modifier
            
        final_value *= percent_modifier / 100
        
        return final_value


rule_consolidator = RuleConsolidator()
