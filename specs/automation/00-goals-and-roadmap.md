# Automation Specs Part 00 - Goals and Roadmap

## Introduction

This is the first in a series of design documents concerning an improved automation system for the game *You're the OS!*. The new system will replace the current implementation of the automation API for the game.

## Current Implementation

The current implementation of automation uses a dedicated entry point for the game in the file `src/auto.py`. This entry point is called with parameters indicating the difficulty level or sandbox config to use along with the filename of an automation script.
