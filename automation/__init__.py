"""Automation package for You're the OS.

This package provides tools for creating automated OS schedulers.

Modules:
    api: Base classes and infrastructure (Scheduler, Page, Process, IoQueue)
    skeleton: Template for creating new automation scripts
    example: A working example scheduler implementation
"""
from .api import Scheduler, Page, Process, IoQueue

__all__ = ['Scheduler', 'Page', 'Process', 'IoQueue']
