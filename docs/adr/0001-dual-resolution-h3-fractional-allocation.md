---
status: accepted
---

# Dual-Resolution Uber H3 Fractional Footprint Allocation

We reconstruct each Thermal Detection's oriented elliptical Instantaneous Footprint ($\Delta S(\theta) \times \Delta T(\theta)$) from spherical scan geometry and allocate its radiative flux fractionally across Uber H3 Iso-Area Cells (Resolution 7 for regional phenology at $\sim 5.16\text{ km}^2$ and Resolution 8 for field tactical analysis at $\sim 0.737\text{ km}^2$), rather than assigning point centroids to a $0.05^\circ$ latitude-longitude grid.

## Considered Options

- **Point-centroid binning on $0.05^\circ$ Climate Modeling Grid (CMG)**: Simple to compute, but $0.05^\circ$ cells shrink by $\cos\phi$ toward higher latitudes and discard VIIRS $375\text{ m}$ sub-kilometer spatial precision.
- **Point-centroid binning on H3**: Preserves equal area globally, but treats an edge-of-swath MODIS pixel ($4.83 \times 2.01\text{ km} = 9.69\text{ km}^2$) as a zero-area point, creating severe spatial aliasing across up to 13 neighboring H3 Resolution 8 cells.
- **Oriented Elliptical Footprint Reconstruction + Fractional H3 Allocation (Chosen)**: Solves the $70\times$ footprint area disparity between nadir VIIRS ($0.138\text{ km}^2$) and edge-of-swath MODIS ($9.69\text{ km}^2$) while strictly conserving areal radiative energy ($\sum_h w_{p,h} = 1$).
