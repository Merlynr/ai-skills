#!/usr/bin/env node
'use strict';
/**
 * Tighten OpenCode /gsd-* slash commands (L1 runtime), separate from skillshare skills/.
 *
 * skillshare include filter → ~/.config/opencode/skills/ (~18 Merlynr facade skills)
 * this script → ~/.config/opencode/command/ (GSD staged commands; default profile=full)
 *
 * Usage:
 *   node script/apply-opencode-gsd-surface.js [--dry-run]
 */

const fs = require('fs');
const os = require('os');
const path = require('path');

const dryRun = process.argv.includes('--dry-run');
const repoRoot = path.resolve(__dirname, '..');

function expandHome(p) {
  if (!p || p[0] !== '~') return p;
  return path.join(os.homedir(), p.slice(1).replace(/^[/\\]/, ''));
}

const opencodeDir = expandHome(
  process.env.OPENCODE_CONFIG_DIR
    || (process.env.XDG_CONFIG_HOME
      ? path.join(process.env.XDG_CONFIG_HOME, 'opencode')
      : path.join(os.homedir(), '.config', 'opencode'))
);

function resolveGsdLib() {
  const candidates = [
    path.join(opencodeDir, 'get-shit-done', 'get-shit-done', 'bin', 'lib'),
    path.join(opencodeDir, 'get-shit-done', 'bin', 'lib'),
    path.join(expandHome('~/.codex/get-shit-done/get-shit-done/bin/lib')),
    path.join(expandHome('~/.codex/get-shit-done/bin/lib')),
    path.join(repoRoot, 'skills/base/_get-shit-done/get-shit-done/bin/lib'),
  ];
  for (const dir of candidates) {
    if (fs.existsSync(path.join(dir, 'surface.cjs'))) return dir;
  }
  throw new Error(
    'GSD surface.cjs not found. Install GSD L1 (npx @opengsd/gsd-core@latest) first.'
  );
}

function resolveCommandsSource() {
  const markerPath = path.join(opencodeDir, '.gsd-source');
  if (fs.existsSync(markerPath)) {
    try {
      const src = fs.readFileSync(markerPath, 'utf8').trim();
      if (src && fs.existsSync(src)) return src;
    } catch {
      /* fall through */
    }
  }
  const candidates = [
    path.join(repoRoot, 'skills/base/_get-shit-done/commands/gsd'),
    path.join(opencodeDir, 'get-shit-done', 'commands', 'gsd'),
    path.join(expandHome('~/.codex/get-shit-done/commands/gsd')),
  ];
  for (const src of candidates) {
    if (fs.existsSync(src)) {
      if (!dryRun) fs.writeFileSync(markerPath, `${src}\n`, 'utf8');
      return src;
    }
  }
  throw new Error(
    'commands/gsd source not found. Run: skillshare update --group base'
  );
}

const libDir = resolveGsdLib();
// eslint-disable-next-line import/no-dynamic-require, global-require
const { resolveRuntimeArtifactLayout } = require(path.join(libDir, 'runtime-artifact-layout.cjs'));
// eslint-disable-next-line import/no-dynamic-require, global-require
const { applySurface, writeSurface, listSurface } = require(path.join(libDir, 'surface.cjs'));
// eslint-disable-next-line import/no-dynamic-require, global-require
const { loadSkillsManifest, writeActiveProfile } = require(path.join(libDir, 'install-profiles.cjs'));
// eslint-disable-next-line import/no-dynamic-require, global-require
const { CLUSTERS } = require(path.join(libDir, 'clusters.cjs'));

/** Merlynr OpenCode L1: help + update only (surface pulls config subgraph). */
const MERLYNR_OPENCODE_SURFACE = {
  baseProfile: 'core',
  disabledClusters: Object.keys(CLUSTERS),
  explicitAdds: ['help', 'update'],
  explicitRemoves: [],
};

function countCommands(dir) {
  if (!fs.existsSync(dir)) return 0;
  return fs.readdirSync(dir).filter((f) => f.startsWith('gsd-') && f.endsWith('.md')).length;
}

function main() {
  if (!fs.existsSync(opencodeDir)) {
    throw new Error(`OpenCode config dir not found: ${opencodeDir}`);
  }

  const commandDir = path.join(opencodeDir, 'command');
  const before = countCommands(commandDir);
  const commandsSource = resolveCommandsSource();
  const manifest = loadSkillsManifest(commandsSource);
  const layout = resolveRuntimeArtifactLayout('opencode', opencodeDir, 'global');

  if (dryRun) {
    console.log('[dry-run] Would apply Merlynr OpenCode GSD surface');
    console.log(`  opencode dir:     ${opencodeDir}`);
    console.log(`  commands source:  ${commandsSource}`);
    console.log(`  gsd lib:          ${libDir}`);
    console.log(`  commands now:     ${before}`);
    console.log(`  retain stems:     ${MERLYNR_OPENCODE_SURFACE.explicitAdds.join(', ')}`);
    return;
  }

  writeActiveProfile(opencodeDir, 'core');
  writeSurface(opencodeDir, MERLYNR_OPENCODE_SURFACE);
  applySurface(opencodeDir, layout, manifest, CLUSTERS);

  const after = countCommands(commandDir);
  const listing = listSurface(opencodeDir, manifest, CLUSTERS);
  console.log(`OpenCode GSD slash commands: ${before} → ${after}`);
  console.log(`Retained: ${listing.enabled.join(', ') || '(none)'}`);
  console.log(
    'Workflow skills: merlynr-dev-stack + gsd-ns-* in ~/.config/opencode/skills/ (skillshare facade)'
  );
}

main();
