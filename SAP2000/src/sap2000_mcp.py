# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.9,<2", "comtypes>=1.4"]
# ///

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.abspath(os.path.join(HERE, '..', '..', 'common'))

# in the repository the shared modules live in common, in a packed bundle they sit next to this file

if os.path.isdir(COMMON):
    sys.path.insert(0, COMMON)

import csi_com

# stdout carries the MCP protocol, so the program header goes to stderr

print('\nSAP2000 MCP server', file=sys.stderr)
print('V.K. Papanikolaou, Assoc. Prof. AUTh', file=sys.stderr)
print('Last updated : 31/10/2026\n', file=sys.stderr)

csi_com.setup('SAP2000')

import csi_tools

DESIGN = {'concrete': ('DesignConcrete', 'StartDesign', 'Concrete Design'),
          'steel': ('DesignSteel', 'StartDesign', 'Steel Design'),
          'cold_formed': ('DesignColdFormed', 'StartDesign', 'Cold Formed'),
          'aluminum': ('DesignAluminum', 'StartDesign', 'Aluminum Design')}

SELFTEST = ['FrameObj.AddByCoord', 'DatabaseTables.GetTableForDisplayArray',
            'DatabaseTables.ApplyEditedTables', 'Analyze.GetCaseStatus',
            'Results.BaseReact', 'Results.ModalPeriod',
            'LoadPatterns.AutoSeismic.SetEurocode82004_1', 'File.Save']

mcp = csi_tools.create('SAP2000', DESIGN, {}, '.sdb, .s2k, .$2k')

if len(sys.argv) == 2 and sys.argv[1] == '--selftest':
    csi_tools.selftest(SELFTEST)

elif len(sys.argv) == 1:
    mcp.run()

else:
    print('Usage : uv run --script sap2000_mcp.py [--selftest]', file=sys.stderr)
    sys.exit(1)
