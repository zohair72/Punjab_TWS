# Methodology

This project is a **Punjab-scale terrestrial water storage anomaly dashboard**.

## Core Scientific Framing

- GRACE/GRACE-FO provides the primary terrestrial water storage anomaly signal.
- GLDAS is included as contextual support data for the same month as newly available GRACE records.
- The core output is regional Punjab-scale interpretation of terrestrial water storage change.

## Scope Limits

- This dashboard does not perform district-level groundwater analytics.
- District boundaries may be displayed only as optional visual reference overlays.
- Outputs are intended for regional interpretation, not local aquifer quantification.

## Update Logic

- GRACE availability controls monthly update timing.
- When a new GRACE month becomes available, the system should also store the matching GLDAS month as context.
- The dashboard should read from stored processed outputs rather than making live Earth Engine calls on each page load.

