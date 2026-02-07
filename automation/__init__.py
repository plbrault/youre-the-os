"""Automation package for You're the OS.

This package provides tools for creating automated OS schedulers.

Modules:
    api: Base classes and infrastructure (RunOs, Page, Process, IoQueue)
    skeleton: Template for creating new automation scripts
    example: A working example scheduler implementation
"""
from .api import RunOs, Page, Process, IoQueue

__all__ = ['RunOs', 'Page', 'Process', 'IoQueue']
