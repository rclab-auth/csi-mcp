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

print('\nETABS MCP server', file=sys.stderr)
print('V.K. Papanikolaou, Assoc. Prof. AUTh', file=sys.stderr)
print('Last updated : 31/10/2026\n', file=sys.stderr)

csi_com.setup('ETABS')

import csi_tools
from csi_com import invoke, run

# shear wall design has no start function in the API, its results are read with DesignShearWall.GetPierSummaryResults
# concrete_shell needs ETABS 23 or newer (DesignConcreteShell)

DESIGN = {'concrete': ('DesignConcrete', 'StartDesign', 'Concrete Frame Design'),
          'steel': ('DesignSteel', 'StartDesign', 'Steel Frame Design'),
          'composite_beam': ('DesignCompositeBeam', 'StartDesign', 'Composite Beam'),
          'composite_column': ('DesignCompositeColumn', 'StartDesign', 'Composite Column'),
          'concrete_slab': ('DesignConcreteSlab', 'StartSlabDesign', 'Slab Design'),
          'concrete_shell': ('DesignConcreteShell', 'StartDesign', 'Shell Design')}

ALIASES = {'story_drifts': 'StoryDrifts', 'joint_drifts': 'JointDrifts',
           'pier_force': 'PierForce', 'spandrel_force': 'SpandrelForce',
           'base_react_centroid': 'BaseReactWithCentroid'}

SELFTEST = ['FrameObj.AddByCoord', 'DatabaseTables.GetTableForDisplayArray',
            'DatabaseTables.ApplyEditedTables', 'Analyze.GetCaseStatus',
            'Results.StoryDrifts', 'Results.PierForce',
            'Story.GetStories_2', 'DesignConcrete.StartDesign',
            'DesignShearWall.GetPierSummaryResults', 'DesignConcreteSlab.StartSlabDesign',
            'DesignCompositeBeam.StartDesign', 'DesignCompositeColumn.StartDesign',
            'File.NewGridOnly', 'File.Save']

mcp = csi_tools.create('ETABS', DESIGN, ALIASES, '.edb, .e2k')

@mcp.tool(description='Story data of the model: name, elevation, height, master story, similar to, splice. Heights in present units.')
async def stories() -> dict:

    def work():

        out = invoke('Story.GetStories_2')['outputs']
        n = out.get('NumberStories') or 0
        cols = {k: v for k, v in out.items() if isinstance(v, list) and len(v) == n}

        return {'base_elevation': out.get('BaseElevation'),
                'count': n,
                'stories': [{k: cols[k][i] for k in cols} for i in range(n)]}

    return await run(work)

if len(sys.argv) == 2 and sys.argv[1] == '--selftest':
    csi_tools.selftest(SELFTEST)

elif len(sys.argv) == 1:
    mcp.run()

else:
    print('Usage : uv run --script etabs_mcp.py [--selftest]', file=sys.stderr)
    sys.exit(1)
