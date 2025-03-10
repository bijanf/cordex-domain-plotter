import argparse

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
from cordex.domain import cordex_domain
from pyproj import Transformer


def plot_domain(domain):
    eur11 = cordex_domain(domain, dummy="topo")

    pollon = eur11.rotated_latitude_longitude.grid_north_pole_longitude
    pollat = eur11.rotated_latitude_longitude.grid_north_pole_latitude

    rlon = eur11.rlon.values
    rlat = eur11.rlat.values

    transformer = Transformer.from_crs(
        ccrs.RotatedPole(pole_longitude=pollon, pole_latitude=pollat).proj4_init,
        ccrs.PlateCarree().proj4_init,
        always_xy=True,
    )

    lon, lat = np.meshgrid(rlon, rlat)
    lon_regular, lat_regular = transformer.transform(lon, lat)

    ll_lon = np.min(lon_regular)
    ll_lat = np.min(lat_regular)
    ur_lon = np.max(lon_regular)
    ur_lat = np.max(lat_regular)

    corners = [
        (ll_lon, ll_lat),
        (ll_lon, ur_lat),
        (ur_lon, ur_lat),
        (ur_lon, ll_lat),
        (ll_lon, ll_lat),
    ]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    ax.set_extent(
        [ll_lon - 5, ur_lon + 5, ll_lat - 5, ur_lat + 5], crs=ccrs.PlateCarree()
    )

    mesh = ax.pcolormesh(
        lon_regular,
        lat_regular,
        eur11.topo,
        transform=ccrs.PlateCarree(),
        cmap="terrain",
        vmin=0,
        vmax=3000,
    )

    lons, lats = zip(*corners)
    ax.plot(
        lons,
        lats,
        transform=ccrs.PlateCarree(),
        color="red",
        linewidth=2,
        label="Bounding Box",
    )

    ax.coastlines(resolution="50m", color="black", linewidth=1)
    ax.add_feature(cfeature.BORDERS, linestyle=":")

    plt.title(f"CORDEX {domain} Domain and Bounding Box")
    plt.legend()

    corner_labels = [
        f"LL: (lon = {ll_lon:.2f},\n lat = {ll_lat:.2f})",
        f"UL: (lon = {ll_lon:.2f},\n lat = {ur_lat:.2f})",
        f"UR: (lon = {ur_lon:.2f},\n lat = {ur_lat:.2f})",
        f"LR: (lon = {ur_lon:.2f},\n lat = {ll_lat:.2f})",
    ]

    ax.text(
        ll_lon,
        ll_lat,
        corner_labels[0],
        transform=ccrs.PlateCarree(),
        fontsize=12,
        color="red",
        ha="right",
        va="bottom",
    )
    ax.text(
        ll_lon,
        ur_lat,
        corner_labels[1],
        transform=ccrs.PlateCarree(),
        fontsize=12,
        color="red",
        ha="right",
        va="top",
    )
    ax.text(
        ur_lon,
        ur_lat,
        corner_labels[2],
        transform=ccrs.PlateCarree(),
        fontsize=12,
        color="red",
        ha="left",
        va="top",
    )
    ax.text(
        ur_lon,
        ll_lat,
        corner_labels[3],
        transform=ccrs.PlateCarree(),
        fontsize=12,
        color="red",
        ha="left",
        va="bottom",
    )

    plt.savefig(
        f"{domain}_domain_map.png", dpi=300, bbox_inches="tight", pad_inches=0.1
    )
    print(corner_labels)
    plt.tight_layout()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot CORDEX domain and bounding box.")
    parser.add_argument("domain", type=str, help="CORDEX domain name (e.g., EUR-11)")
    args = parser.parse_args()
    plot_domain(args.domain)
