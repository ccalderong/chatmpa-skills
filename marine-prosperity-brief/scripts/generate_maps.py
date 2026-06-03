#!/usr/bin/env python3
"""Generate two-panel location maps for Gulf of California communities."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import numpy as np
import os
from chatmpa.brand import COLORS, mpl_theme

matplotlib.rcParams.update(mpl_theme())

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'maps')
os.makedirs(OUTPUT_DIR, exist_ok=True)

COMMUNITIES = {
    'alto_golfo': {
        'name': 'San Felipe',
        'lon': -114.840, 'lat': 31.017,
        'state': 'Baja California'
    },
    'bahia_de_banderas': {
        'name': 'Bahía de Banderas',
        'lon': -105.372065, 'lat': 20.627889,
        'state': 'Nayarit / Jalisco',
        # Pacific coast — use its own regional extent instead of the Gulf view
        'regional_extent': [-110, -102, 18, 24],
    },
    'bahia_de_los_angeles': {
        'name': 'Bahía de Los Ángeles',
        'lon': -113.557319, 'lat': 28.952243,
        'state': 'Baja California'
    },
    'bahia_de_kino': {
        'name': 'Bahía de Kino',
        'lon': -111.988162, 'lat': 28.849950,
        'state': 'Sonora'
    },
    'el_manglito': {
        'name': 'El Manglito',
        'lon': -110.332784, 'lat': 24.147043,
        'state': 'Baja California Sur'
    },
    'la_manga': {
        'name': 'La Manga',
        'lon': -111.125412, 'lat': 27.977831,
        'state': 'Sonora'
    },
    'la_reforma': {
        'name': 'La Reforma',
        'lon': -108.054608, 'lat': 25.079383,
        'state': 'Sinaloa'
    },
    'la_ribera': {
        'name': 'La Ribera',
        'lon': -109.583339, 'lat': 23.596448,
        'state': 'Baja California Sur'
    },
    'punta_chueca': {
        'name': 'Punta Chueca',
        'lon': -112.161351, 'lat': 29.012642,
        'state': 'Sonora'
    },
    'san_basilio': {
        'name': 'San Basilio',
        'lon': -111.422032, 'lat': 26.372312,
        'state': 'Sonora'
    },
    'san_carlos': {
        'name': 'San Carlos',
        'lon': -111.077044, 'lat': 27.939255,
        'state': 'Sonora'
    },
}

# Default regional bounding box (Gulf of California)
GOC_EXTENT = [-118, -105, 21, 33]  # [west, east, south, north]
MEXICO_EXTENT = [-118, -86, 14, 33]  # Mexico national extent


def add_north_arrow(ax, x=0.05, y=0.92, size=0.04):
    ax.annotate('N', xy=(x, y), xycoords='axes fraction',
                fontsize=9, ha='center', va='bottom', fontweight='bold')
    ax.annotate('', xy=(x, y), xycoords='axes fraction',
                xytext=(x, y - size), textcoords='axes fraction',
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))


def make_regional_panel(ax, com_lon, com_lat, com_name, regional_extent=None):
    extent = regional_extent if regional_extent is not None else GOC_EXTENT
    ax.set_extent(extent, crs=ccrs.PlateCarree())

    # Background ocean
    ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor=COLORS["light_blue"], zorder=0)
    ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor=COLORS["sand"], zorder=1)
    ax.add_feature(cfeature.COASTLINE.with_scale('10m'), linewidth=0.6,
                   edgecolor=COLORS["text_dark"], zorder=2)
    ax.add_feature(cfeature.BORDERS.with_scale('10m'), linewidth=0.5,
                   edgecolor=COLORS["text_gray"], linestyle='--', zorder=2)
    ax.add_feature(cfeature.STATES.with_scale('10m'), linewidth=0.35,
                   edgecolor=COLORS["text_gray"], zorder=2)
    ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor=COLORS["light_blue"], zorder=2)

    # Plot all communities as small dots
    for key, c in COMMUNITIES.items():
        if c['name'] == com_name:
            continue
        ax.plot(c['lon'], c['lat'], marker='o', color=COLORS["text_gray"], markersize=3,
                transform=ccrs.PlateCarree(), zorder=4, alpha=0.7)

    # Plot target community as red star
    ax.plot(com_lon, com_lat, marker='*', color=COLORS["coral"], markersize=14,
            markeredgecolor='white', markeredgewidth=0.8,
            transform=ccrs.PlateCarree(), zorder=5)
    ax.text(com_lon + 0.35, com_lat + 0.2, com_name,
            transform=ccrs.PlateCarree(), fontsize=8, fontweight='bold',
            color=COLORS["coral"], zorder=6,
            path_effects=[pe.withStroke(linewidth=2, foreground='white')])

    # Gridlines
    gl = ax.gridlines(draw_labels=True, linewidth=0.4, color='gray',
                      alpha=0.5, linestyle='--', x_inline=False, y_inline=False)
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 7}
    gl.ylabel_style = {'size': 7}

    # Scale bar — placed in the bottom-left corner of whatever extent is used
    sb_lon = extent[0] + 0.5                   # 0.5° from western edge
    sb_lat = extent[2] + 0.3                   # 0.3° from southern edge
    ax.plot([sb_lon, sb_lon + 1.0], [sb_lat, sb_lat], 'k-', linewidth=2,
            transform=ccrs.PlateCarree(), zorder=6)
    ax.text(sb_lon + 0.5, sb_lat - 0.3, '~111 km', transform=ccrs.PlateCarree(),
            fontsize=6.5, ha='center', zorder=6)

    region_label = 'A. Pacific Coast Region' if regional_extent is not None else 'A. Gulf of California Region'
    add_north_arrow(ax)
    ax.set_title(region_label, fontsize=9, fontweight='bold', pad=4)


def make_inset_panel(ax, com_lon, com_lat, regional_extent=None):
    ax.set_extent(MEXICO_EXTENT, crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.OCEAN.with_scale('50m'), facecolor=COLORS["light_blue"], zorder=0)
    ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor=COLORS["sand"], zorder=1)
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.5,
                   edgecolor=COLORS["text_dark"], zorder=2)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.6,
                   edgecolor=COLORS["text_dark"], zorder=2)

    # Highlight the regional extent used in the main panel
    extent = regional_extent if regional_extent is not None else GOC_EXTENT
    region_rect = mpatches.Rectangle(
        (extent[0], extent[2]),
        extent[1] - extent[0],
        extent[3] - extent[2],
        linewidth=1.2, edgecolor=COLORS["coral"],
    facecolor=(*mcolors.to_rgb(COLORS["coral"]), 0.12),
        transform=ccrs.PlateCarree(), zorder=3
    )
    ax.add_patch(region_rect)

    # Mark community
    ax.plot(com_lon, com_lat, marker='*', color=COLORS["coral"], markersize=8,
            markeredgecolor='white', markeredgewidth=0.5,
            transform=ccrs.PlateCarree(), zorder=4)

    ax.set_title('B. Mexico', fontsize=8, fontweight='bold', pad=3)
    ax.set_xticks([])
    ax.set_yticks([])


def generate_map(slug, community):
    fig = plt.figure(figsize=(8, 4.5), dpi=150)

    # Leave ~10% at top for panel titles, 8% at bottom for axis labels
    ax_main = fig.add_axes([0.02, 0.08, 0.62, 0.80],
                           projection=ccrs.Mercator())
    ax_inset = fig.add_axes([0.67, 0.12, 0.30, 0.68],
                            projection=ccrs.Mercator())

    regional_extent = community.get('regional_extent', None)
    make_regional_panel(ax_main, community['lon'], community['lat'],
                        community['name'], regional_extent=regional_extent)
    make_inset_panel(ax_inset, community['lon'], community['lat'],
                     regional_extent=regional_extent)

    outpath = os.path.join(OUTPUT_DIR, f'{slug}_location_map.png')
    fig.savefig(outpath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  Saved: {os.path.basename(outpath)}')
    return outpath


if __name__ == '__main__':
    print('Generating location maps...')
    for slug, community in COMMUNITIES.items():
        try:
            generate_map(slug, community)
        except Exception as e:
            print(f'  ERROR for {slug}: {e}')
    print('Done.')
