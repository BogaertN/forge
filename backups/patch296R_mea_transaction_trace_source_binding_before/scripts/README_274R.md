# Patch 274R — Startup Terminus Containment Fix

Purpose: final-product startup should open only the clean AI.Web Operator Console app window. The high-security Terminus shell remains hidden until the operator opens it from inside the Operator Console.

This patch corrects the legacy desktop launcher path that still opened the old visible-terminal / standalone Terminus surface. It also teaches the appctl stop/restart path to close any future appctl-owned standalone Terminus shell pidfile at the same time as the Operator Console and backend.

Safety boundary:
- no browser shell authority
- no arbitrary command endpoint
- no RMC memory write
- no Identity Vault write
- no Chroma write
- no LLM call
- no unsafe process scan that kills normal Chrome windows

Important limitation: if a normal personal Chrome window already has a manually opened `localhost:7477` tab, Patch 274R will not kill that entire browser window because that could close unrelated work. Future startup will not create that tab.
