# Changelog

All notable changes to the **AI Frontier Matrix** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.1.0] - 2026-11-26

### 📱 Mobile UI/UX Redesign & Architecture Overhaul
- **Ultra-Compact Milestone Tiles**: Redesigned mobile timeline cards from ~140px tall paragraphs into sleek 46px compact tiles showing Brand Logo, Model Name, Release Date, and touch chevron `›`. Allows viewing 5-8 milestones on a single mobile screen.
- **Brand Logo Icon Filter Bar**: Replaced wrapping text pill filters on mobile with 6 clean, squircle circular icon buttons (`⏳ All`, `✦ Gemini`, `ChatGPT`, `Claude`, `Qwen`, `Mistral`), all fitting neatly on a single centered row with zero line-wrapping.
- **Interactive Detail Modal (Bottom-Sheet / Dialog)**: Added `#model-detail-modal` popup triggered when tapping any model tile. Features backdrop blur, tactile mobile grabber handle, 4-cell technical specs grid (Context Window, Modalities, Access Plan, System ID), and full capabilities description text.
- **Eliminated Top Header Duplication**: Removed the redundant `.mobile-layer-segment` in the mobile header, keeping the top bar slim (42px) and leaving all layer navigation to the thumb-friendly bottom dock.
- **Bilingual Popup Support**: Full Chinese and English localized labels for modal specs and action buttons.

---

## [v1.0.0] - 2026-11-25

### 🚀 Initial Official Release
- **Global Top Labs Model Matrix**: Full frontier spectrum tracking for Google DeepMind (Gemini), OpenAI (ChatGPT), Anthropic (Claude), Alibaba (Qwen), and Mistral AI.
- **AI Coding Agents Matrix**: Dedicated layer tracking release changelogs for Google Antigravity Desktop, OpenAI Codex CLI, Claude Code, Alibaba Qwen Code, and Mistral Vibe.
- **Autonomous Cloud Sync**: Dynamic epoch parsing, real-time model verification, and client-side caching.
- **Bilingual Interface**: Seamless one-click English and Chinese (`EN` / `中文`) language switching.
- **Zero-Dependency Architecture**: Standalone, self-contained single-page responsive web application running on GitHub Pages.
- **Brand Attribution**: Official branding with `Wil Chew@2026`.
