# -*- mode: python ; coding: utf-8 -*-
"""Spec PyInstaller du build autonome de Pac-Man.

Construit avec :  make package
"""

analysis = Analysis(  # noqa: F821  (injecte par PyInstaller)
    ["launcher.py"],
    pathex=["."],
    binaries=[],
    # (source, destination dans le bundle). Les chemins de destination
    # reproduisent l'arborescence du depot, car le code retrouve ses fichiers
    # relativement a __file__.
    datas=[
        ("Assets", "Assets"),
        ("src/ui/font_pacman", "src/ui/font_pacman"),
        ("config.json", "."),
        # Instructions livrees avec le jeu, exigees par le sujet.
        ("INSTRUCTIONS.txt", "."),
    ],
    hiddenimports=["mazegenerator"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Modules de developpement : inutiles dans le build livre.
    excludes=["flake8", "mypy", "pytest", "tkinter"],
    noarchive=False,
)

archive = PYZ(analysis.pure)  # noqa: F821

executable = EXE(  # noqa: F821
    archive,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="pacman",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

collection = COLLECT(  # noqa: F821
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="pacman",
)

# Sur macOS, produit en plus un .app double-cliquable.
app = BUNDLE(  # noqa: F821
    collection,
    name="Pac-Man.app",
    icon=None,
    bundle_identifier="fr.42.pacman",
)
