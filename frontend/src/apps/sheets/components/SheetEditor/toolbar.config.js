import { translate as __ } from '@/boot/translation'
// Pure config factories for SheetEditor toolbar dropdowns.
// Each factory takes a map of action callbacks and returns a Frappe UI Dropdown options array.

export function buildAlignOptions({ setAlign, setValign }) {
  return [
    { group: __('Horizontal'), options: [
      { label: __('Left'),   icon: 'lucide-align-left',   onClick: () => setAlign('left')   },
      { label: __('Center'), icon: 'lucide-align-center', onClick: () => setAlign('center') },
      { label: __('Right'),  icon: 'lucide-align-right',  onClick: () => setAlign('right')  },
    ]},
    { group: __('Vertical'), options: [
      { label: __('Top'),    icon: 'lucide-arrow-up',   onClick: () => setValign('top')    },
      { label: __('Middle'), icon: 'lucide-minus', onClick: () => setValign('middle') },
      { label: __('Bottom'), icon: 'lucide-arrow-down', onClick: () => setValign('bottom') },
    ]},
  ]
}

export function buildBorderOptions({ applyBorder }) {
  return [
    { group: __('Apply to selection'), options: [
      { label: __('All borders'),     icon: 'lucide-grid-2x2', onClick: () => applyBorder('all')     },
      { label: __('Outside borders'), icon: 'lucide-square',   onClick: () => applyBorder('outside') },
      { label: __('Inner borders'),   icon: 'lucide-plus',     onClick: () => applyBorder('inner')   },
    ]},
    { group: __('Single side'), options: [
      { label: __('Top border'),    icon: 'lucide-arrow-up',    onClick: () => applyBorder('top')    },
      { label: __('Bottom border'), icon: 'lucide-arrow-down',  onClick: () => applyBorder('bottom') },
      { label: __('Left border'),   icon: 'lucide-arrow-left',  onClick: () => applyBorder('left')   },
      { label: __('Right border'),  icon: 'lucide-arrow-right', onClick: () => applyBorder('right')  },
    ]},
    { group: __('Remove'), options: [
      { label: __('No border'), icon: 'lucide-square-x', theme: 'red', onClick: () => applyBorder('none') },
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
    { group: __('Format'), options: [
      { label: __('Strikethrough'),    icon: 'lucide-strikethrough', onClick: () => toggleFmt('strikethrough') },
      { label: __('Wrap text'),        icon: 'lucide-corner-down-left', onClick: () => toggleWrap()              },
      { label: __('Format painter'),   icon: 'lucide-paint-roller',  onClick: () => toggleFormatPainter()     },
      { label: __('Clear formatting'), icon: 'lucide-eraser',        onClick: () => clearFormatting()         },
    ]},
    { group: __('Numbers'), options: [
      { label: __('Decrease decimal places'), icon: 'lucide-minus', onClick: () => adjustDecimals(-1) },
      { label: __('Increase decimal places'), icon: 'lucide-plus',  onClick: () => adjustDecimals(+1) },
    ]},
    { group: __('Cells'), options: [
      { label: __('Conditional formatting'), icon: 'lucide-blend', onClick: () => openCfDialog(null)        },
      { label: __('Insert hyperlink'),       icon: 'lucide-link',  onClick: () => openHyperlinkDialog()     },
      { label: __('Merge / unmerge'),        icon: 'lucide-maximize-2', onClick: () => toggleMerge()             },
      { label: __('Toggle filter'),          icon: 'lucide-filter',     onClick: () => toggleSortFilter()        },
      { label: __('Smart Fill (Ctrl+E)'),    icon: 'lucide-zap',        onClick: () => runSmartFill?.()          },
    ]},
    { group: __('Borders'), options: [
      { label: __('All borders'),     icon: 'lucide-grid-2x2', onClick: () => applyBorder('all')     },
      { label: __('Outside borders'), icon: 'lucide-square',   onClick: () => applyBorder('outside') },
      { label: __('No border'),       icon: 'lucide-square-x', onClick: () => applyBorder('none')    },
    ]},
    { group: __('View'), options: [
      { label: __('Zoom in'),    icon: 'lucide-zoom-in',  onClick: () => zoomBy(+0.1)  },
      { label: __('Zoom out'),   icon: 'lucide-zoom-out', onClick: () => zoomBy(-0.1)  },
      { label: __('Reset zoom'), icon: 'lucide-minimize', onClick: () => resetZoom()   },
    ]},
    { group: __('Insert'), options: [
      { label: __('Pivot table…'), icon: 'lucide-layout',      onClick: () => openPivotDialog() },
      { label: __('Chart…'),       icon: 'lucide-chart-bar',   onClick: () => openChartDialog() },
    ]},
    { group: __('Workbook'), options: [
      { label: __('Named ranges…'), icon: 'lucide-bookmark', onClick: () => openNamedRangesDialog() },
    ]},
  ]
}
