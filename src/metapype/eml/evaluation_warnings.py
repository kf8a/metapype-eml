#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: evaluate.py

:Synopsis:

:Author:
    ide

:Created:
    6/24/20
"""
from enum import Enum, auto


class EvaluationWarning(Enum):
    CONNECTION_DEFINITION_DESCRIPTION_MISSING = auto()
    DATASET_ABSTRACT_MISSING = auto()
    DATASET_ABSTRACT_TOO_SHORT = auto()
    DATASET_COVERAGE_MISSING = auto()
    DATASET_METHOD_STEPS_MISSING = auto()
    DATASET_PROJECT_MISSING = auto()
    DATATABLE_DESCRIPTION_MISSING = auto()
    DATATABLE_MISSING = auto()
    DESIGN_DESCRIPTION_DESCRIPTION_MISSING = auto()
    INDIVIDUAL_NAME_INCOMPLETE = auto()
    INTELLECTUAL_RIGHTS_MISSING = auto()
    KEYWORDS_MISSING = auto()
    KEYWORDS_INSUFFICIENT = auto()
    MAINTENANCE_DESCRIPTION_MISSING = auto()
    METHOD_STEP_DESCRIPTION_MISSING = auto()
    ORCID_ID_MISSING = auto()
    OTHER_ENTITY_DESCRIPTION_MISSING = auto()
    PROCEDURE_STEP_DESCRIPTION_MISSING = auto()
    QUALITY_CONTROL_DESCRIPTION_MISSING = auto()
    SAMPLING_DESCRIPTION_DESCRIPTION_MISSING = auto()
    STUDY_EXTENT_DESCRIPTION_MISSING = auto()
    TITLE_TOO_SHORT = auto()
    USER_ID_MISSING = auto()

