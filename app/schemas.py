"""HTTP API 的 Pydantic 模型。"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ConflictPolicy = Literal["collect_all", "priority", "first_hit"]


class RuleIn(BaseModel):
    code: str = Field(..., min_length=1, description="规则编码")
    name: str | None = None
    description: str | None = None
    priority: int = 0
    conflict_group: str | None = None
    conflict_policy: ConflictPolicy | None = None
    depends_on: list[str] = Field(default_factory=list)
    condition: str = Field("", description="条件表达式；空串视为恒真")
    action: str | None = Field(None, description="动作表达式，命中时求值")


class RulesetCreate(BaseModel):
    id: str | None = Field(None, description="可选自定义 ID")
    name: str = Field(..., min_length=1)
    description: str = ""
    default_conflict_policy: ConflictPolicy = "collect_all"
    rules: list[RuleIn] = Field(..., min_length=1)


class RulesetUpdate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    default_conflict_policy: ConflictPolicy = "collect_all"
    rules: list[RuleIn] = Field(..., min_length=1)


class RulesetMeta(BaseModel):
    id: str
    name: str
    description: str
    default_conflict_policy: ConflictPolicy
    current_version: int
    created_at: str
    updated_at: str


class RuleOut(BaseModel):
    code: str
    name: str
    description: str = ""
    priority: int = 0
    conflict_group: str | None = None
    conflict_policy: ConflictPolicy | None = None
    depends_on: list[str] = []
    condition: str = ""
    action: str | None = None
    referenced_rules: list[str] = []


class RulesetVersionOut(BaseModel):
    id: str
    ruleset_id: str
    version: int
    name: str
    description: str
    default_conflict_policy: ConflictPolicy
    rules: list[RuleOut]
    evaluation_order: list[str]
    created_at: str


class EvaluateRequest(BaseModel):
    document: Any = Field(default_factory=dict)


class ConflictExplanation(BaseModel):
    group: str | None = None
    policy: str
    winner: str | None = None
    suppressed: list[dict[str, Any]] = []
    field: str | None = None
    previous_winner: str | None = None
    reason: str | None = None


class RuleTrace(BaseModel):
    rule_code: str
    hit: bool
    value: Any = None
    error: str | None = None


class EvaluationOut(BaseModel):
    id: str
    ruleset_id: str
    version: int
    document: Any
    fired_rule_codes: list[str]
    hit_rule_codes: list[str]
    evaluation_order: list[str]
    iterations: int
    converged: bool
    decision: dict[str, Any]
    conflicts: list[dict[str, Any]]
    traces: list[dict[str, Any]]
    created_at: str


class RecomputeRequest(BaseModel):
    document: Any | None = Field(
        None, description="为空则使用该规则集上一次决策的文档"
    )


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = {}


class EvaluateBatchRequest(BaseModel):
    documents: list[Any] = Field(
        ..., min_length=1, max_length=100, description="待决策文档数组，单次最多 100 项"
    )
    version: int | None = Field(
        None, ge=1, description="指定规则版本；默认当前最新版。整批固定使用同一版本"
    )


class EvaluateBatchItem(BaseModel):
    index: int = Field(..., description="输入 documents 中的下标")
    ok: bool
    result: dict[str, Any] | None = Field(None, description="ok=true 时的决策结果")
    error: ErrorResponse | None = Field(None, description="ok=false 时的错误信息")


class EvaluateBatchResponse(BaseModel):
    ruleset_id: str
    version: int
    success_count: int
    error_count: int
    results: list[EvaluateBatchItem]
