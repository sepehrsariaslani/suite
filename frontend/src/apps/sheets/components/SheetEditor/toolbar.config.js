// Pure config factories for SheetEditor toolbar dropdowns.
// Each factory takes a map of action callbacks and returns a Frappe UI Dropdown options array.

export function buildAlignOptions({ setAlign, setValign }) {
  return [
    { group: __('Horizontal'), items: [
      { label: __('Left'),   icon: 'align-left',   onClick: () => setAlign('left')   },
      { label: __('Center'), icon: 'align-center', onClick: () => setAlign('center') },
      { label: __('Right'),  icon: 'align-right',  onClick: () => setAlign('right')  },
    ]},
    { group: __('Vertical'), items: [
      { label: __('Top'),    icon: 'arrow-up',   onClick: () => setValign('top')    },
      { label: __('Middle'), icon: 'minus',      onClick: () => setValign('middle') },
      { label: __('Bottom'), icon: 'arrow-down', onClick: () => setValign('bottom') },
    ]},
  ]
}

export function buildBorderOptions({ applyBorder }) {
  return [
    { group: __('Apply to selection'), items: [
      { label: __('All borders'),     icon: 'grid',         onClick: () => applyBorder('all')     },
      { label: __('Outside borders'), icon: 'square',       onClick: () => applyBorder('outside') },
      { label: __('Inner borders'),   icon: 'plus',         onClick: () => applyBorder('inner')   },
    ]},
    { group: __('Single side'), items: [
      { label: __('Top border'),    icon: 'arrow-up',    onClick: () => applyBorder('top')    },
      { label: __('Bottom border'), icon: 'arrow-down',  onClick: () => applyBorder('bottom') },
      { label: __('Left border'),   icon: 'arrow-left',  onClick: () => applyBorder('left')   },
      { label: __('Right border'),  icon: 'arrow-right', onClick: () => applyBorder('right')  },
    ]},
    { group: __('Remove'), items: [
      { label: __('No border'), icon: 'x-square', theme: 'red', onClick: () => applyBorder('none') },
    ]},
  ]
}

export function buildMoreToolbarOptions({
  toggleFmt, toggleWrap, toggleFormatPainter, clearFormatting,
  adjustDecimals, openCfDialog, openHyperlinkDialog, toggleMerge,
  toggleSortFilter, applyBorder, zoomBy, resetZoom, openPivotDialog,
  openChartDialog, openNamedRangesDialog, runSmartFill,
}) {
  return [
    { group: __('Format'), items: [
      { label: __('Strikethrough'),    icon: 'lucide-strikethrough', onClick: () => toggleFmt('strikethrough') },
      { label: __('Wrap text'),        icon: 'corner-down-left',     onClick: () => toggleWrap()              },
      { label: __('Format painter'),   icon: 'lucide-paint-roller',  onClick: () => toggleFormatPainter()     },
      { label: __('Clear formatting'), icon: 'lucide-eraser',        onClick: () => clearFormatting()         },
    ]},
    { group: __('Numbers'), items: [
      { label: __('Decrease decimal places'), icon: 'minus', onClick: () => adjustDecimals(-1) },
      { label: __('Increase decimal places'), icon: 'plus',  onClick: () => adjustDecimals(+1) },
    ]},
    { group: __('Cells'), items: [
      { label: __('Conditional formatting'), icon: 'lucide-blend', onClick: () => openCfDialog(null)        },
      { label: __('Insert hyperlink'),       icon: 'lucide-link',  onClick: () => openHyperlinkDialog()     },
      { label: __('Merge / unmerge'),        icon: 'maximize-2',   onClick: () => toggleMerge()             },
      { label: __('Toggle filter'),          icon: 'filter',       onClick: () => toggleSortFilter()        },
      { label: __('Smart Fill (Ctrl+E)'),    icon: 'zap',          onClick: () => runSmartFill?.()          },
    ]},
    { group: __('Borders'), items: [
      { label: __('All borders'),     icon: 'grid',     onClick: () => applyBorder('all')     },
      { label: __('Outside borders'), icon: 'square',   onClick: () => applyBorder('outside') },
      { label: __('No border'),       icon: 'x-square', onClick: () => applyBorder('none')    },
    ]},
    { group: __('View'), items: [
      { label: __('Zoom in'),    icon: 'zoom-in',  onClick: () => zoomBy(+0.1)  },
      { label: __('Zoom out'),   icon: 'zoom-out', onClick: () => zoomBy(-0.1)  },
      { label: __('Reset zoom'), icon: 'minimize', onClick: () => resetZoom()   },
    ]},
    { group: __('Insert'), items: [
      { label: __('Pivot table…'), icon: 'layout',      onClick: () => openPivotDialog() },
      { label: __('Chart…'),       icon: 'bar-chart-2', onClick: () => openChartDialog() },
    ]},
    { group: __('Workbook'), items: [
      { label: __('Named ranges…'), icon: 'bookmark', onClick: () => openNamedRangesDialog() },
    ]},
  ]
}
