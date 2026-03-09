import React, { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'

export interface Project {
  name: string
  technologies: string[]
}

/**
 * TECH_PURPOSES — maps each technology node ID to a plain-English description
 * of its role in this project.
 *
 * WHY THIS EXISTS: The D3 tooltip reads from this object when a user hovers
 * over a node. Without it every node falls back to the generic string
 * "Core technology", making the graph useless as a learning tool.
 *
 * HOW TO EXTEND: Add a new entry whose key exactly matches the string used in
 * the `technologies` array of the Project prop passed to <TechStackGraph>.
 * Keys are case-sensitive.
 */
export const TECH_PURPOSES: Record<string, string> = {
  // ── Frontend ──────────────────────────────────────────────────────────────
  React: 'UI component library — drives every interactive view in the portfolio app',
  TypeScript: 'Typed superset of JavaScript — catches errors at compile time instead of runtime',
  Vite: 'Lightning-fast dev server and bundler — replaces Webpack for near-instant HMR',
  'Tailwind CSS': 'Utility-first CSS framework — styles are written inline as class names, no separate CSS files needed',
  TailwindCSS: 'Utility-first CSS framework — styles are written inline as class names, no separate CSS files needed',
  'D3.js': 'Data-driven SVG rendering library — powers the force-directed tech-stack graph you are looking at now',
  D3: 'Data-driven SVG rendering library — powers the force-directed tech-stack graph you are looking at now',
  Axios: 'Promise-based HTTP client — handles all API requests with automatic JSON parsing and interceptors',
  'React Router': 'Client-side routing library — maps URL paths to page components without full page reloads',
  'React Calendar': 'Accessible calendar UI — used in the Photos page to browse photos by date',
  'React Window': 'Windowed list renderer — renders only visible rows for large photo grids, preventing DOM bloat',
  'date-fns': 'Lightweight date utility library — formats and compares dates without the full Moment.js bundle',
  PostCSS: 'CSS transformation pipeline — runs Tailwind and autoprefixer during the Vite build',
  ESLint: 'Static code linter — enforces consistent TypeScript/React patterns across all source files',
  Prettier: 'Opinionated code formatter — eliminates style debates by auto-formatting on save',

  // ── Backend ───────────────────────────────────────────────────────────────
  FastAPI: 'Modern Python API framework — auto-generates OpenAPI docs and validates requests via Pydantic',
  Python: 'Primary backend language — drives FastAPI, SQLAlchemy, and all simulation services',
  SQLAlchemy: 'Python ORM — maps database tables to Python classes and handles async queries',
  PostgreSQL: 'Production relational database — stores users, content, photos, and simulation state',
  Alembic: 'Database migration tool for SQLAlchemy — tracks schema changes in version-controlled scripts',
  Pydantic: 'Data validation library — defines request/response schemas and enforces types at the API boundary',
  Uvicorn: 'ASGI server — runs FastAPI with async support and powers hot-reload in development',
  bcrypt: 'Password hashing algorithm — one-way hashes passwords so plain text is never stored',
  'python-jose': 'JWT library for Python — signs and verifies authentication tokens sent to the frontend',
  Passlib: 'Password hashing toolkit — wraps bcrypt and provides a consistent hashing context',
  AsyncPG: 'High-performance async PostgreSQL driver — used by SQLAlchemy for non-blocking DB queries',
  Pillow: 'Python image processing library — resizes, rotates, and extracts EXIF metadata from uploaded photos',

  // ── Infrastructure ────────────────────────────────────────────────────────
  Docker: 'Container runtime — packages the app and all its dependencies into portable, reproducible images',
  Terraform: 'Infrastructure-as-Code tool — provisions AWS resources (VPC, RDS, ECS) from declarative HCL files',
  Kubernetes: 'Container orchestration platform — manages deployment scaling, rolling updates, and self-healing',
  K8s: 'Container orchestration platform — manages deployment scaling, rolling updates, and self-healing',
  Ansible: 'Agentless configuration management — applies server configuration via YAML playbooks over SSH',
  'GitHub Actions': 'CI/CD automation — runs linting, tests, and deployments on every pull request and merge',

  // ── Observability ─────────────────────────────────────────────────────────
  Prometheus: 'Time-series metrics collector — scrapes /metrics endpoints and stores performance data',
  Grafana: 'Metrics visualisation dashboard — queries Prometheus to display charts, latency graphs, and alerts',
  OpenTelemetry: 'Vendor-neutral observability SDK — instruments the FastAPI app for distributed tracing',
  OTel: 'Vendor-neutral observability SDK — instruments the FastAPI app for distributed tracing',

  // ── Testing ───────────────────────────────────────────────────────────────
  Pytest: 'Python test framework — runs unit and integration tests against the FastAPI backend',
  Vitest: 'Vite-native unit test runner — shares the same config as the build tool for fast in-browser tests',
  Playwright: 'End-to-end browser automation — runs real user-flow tests across Chromium, Firefox, and WebKit',

  // ── Security ──────────────────────────────────────────────────────────────
  JWT: 'JSON Web Token standard — encodes user identity in a signed, stateless token passed with every request',
}

/**
 * TECHNOLOGY_TAGS — maps each technology node ID to one or more category
 * labels used for filtering the graph.
 *
 * WHY THIS EXISTS: The parent component can pass an `activeTag` prop
 * (e.g. 'frontend', 'testing') and the graph dims all nodes whose tags
 * do NOT include that value. Without this map every node lookup returns
 * `undefined`, so EVERY node is always fully visible — the filter does nothing.
 *
 * VALID TAGS (keep consistent across entries):
 *   'frontend' | 'backend' | 'infrastructure' | 'testing'
 *   'database' | 'observability' | 'security' | 'language'
 */
export const TECHNOLOGY_TAGS: Record<string, string[]> = {
  // ── Frontend ──────────────────────────────────────────────────────────────
  React: ['frontend'],
  TypeScript: ['frontend', 'language'],
  Vite: ['frontend'],
  'Tailwind CSS': ['frontend'],
  TailwindCSS: ['frontend'],
  'D3.js': ['frontend'],
  D3: ['frontend'],
  Axios: ['frontend'],
  'React Router': ['frontend'],
  'React Calendar': ['frontend'],
  'React Window': ['frontend'],
  'date-fns': ['frontend'],
  PostCSS: ['frontend'],
  ESLint: ['frontend'],
  Prettier: ['frontend'],

  // ── Backend ───────────────────────────────────────────────────────────────
  FastAPI: ['backend'],
  Python: ['backend', 'language'],
  SQLAlchemy: ['backend', 'database'],
  PostgreSQL: ['database'],
  Alembic: ['backend', 'database'],
  Pydantic: ['backend'],
  Uvicorn: ['backend'],
  bcrypt: ['backend', 'security'],
  'python-jose': ['backend', 'security'],
  Passlib: ['backend', 'security'],
  AsyncPG: ['backend', 'database'],
  Pillow: ['backend'],

  // ── Infrastructure ────────────────────────────────────────────────────────
  Docker: ['infrastructure'],
  Terraform: ['infrastructure'],
  Kubernetes: ['infrastructure'],
  K8s: ['infrastructure'],
  Ansible: ['infrastructure'],
  'GitHub Actions': ['infrastructure'],

  // ── Observability ─────────────────────────────────────────────────────────
  Prometheus: ['observability'],
  Grafana: ['observability'],
  OpenTelemetry: ['observability'],
  OTel: ['observability'],

  // ── Testing ───────────────────────────────────────────────────────────────
  Pytest: ['testing'],
  Vitest: ['testing'],
  Playwright: ['testing'],

  // ── Security ──────────────────────────────────────────────────────────────
  JWT: ['security'],
}

interface TechStackGraphProps {
  project: Project
  activeTag: string | null
}

interface NodeData extends d3.SimulationNodeDatum {
  id: string
  group: number
  radius: number
  x?: number
  y?: number
  fx?: number | null
  fy?: number | null
}

interface LinkData extends d3.SimulationLinkDatum<NodeData> {}

/**
 * Tooltip — internal display card that appears on node hover/click.
 *
 * It reads from TECH_PURPOSES for the description text and links to
 * documentation via a Google search URL (good enough for a portfolio demo).
 *
 * NOTE: This is a *different* component from the global `Tooltip` in
 * `src/components/Tooltip.tsx`. This one is co-located here because it needs
 * direct access to `TECH_PURPOSES` and is tightly coupled to the graph logic.
 *
 * `tooltipData` is null when no node is hovered/clicked, which causes the
 * component to render nothing (early return null).
 */
const Tooltip: React.FC<{
  tooltipData: { data: NodeData; position: { top: number; left: number } } | null
}> = ({ tooltipData }) => {
  if (!tooltipData) return null

  const purpose =
    TECH_PURPOSES[tooltipData.data.id] ||
    (tooltipData.data.group === 0 ? 'Project Hub' : 'Core technology')
  const learnMoreLink = `https://www.google.com/search?q=${encodeURIComponent(
    tooltipData.data.id,
  )}+documentation`

  return (
    <div
      className="fixed p-4 text-sm bg-gray-900 border border-gray-700 text-white rounded-md shadow-lg z-10 max-w-xs pointer-events-none transition-opacity duration-200"
      style={{
        top: tooltipData.position.top,
        left: tooltipData.position.left,
        transform: 'translate(15px, 15px)',
      }}
    >
      <h4 className="font-bold text-base text-teal-400">{tooltipData.data.id}</h4>

      <div className="mt-2 border-t border-gray-700 pt-2">
        <p className="text-xs text-gray-400 uppercase font-semibold mb-1">Purpose</p>
        <p className="text-gray-300">{purpose}</p>
      </div>

      {tooltipData.data.group !== 0 && (
        <a
          href={learnMoreLink}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-400 hover:underline text-xs mt-2 inline-block pointer-events-auto"
        >
          Learn More &rarr;
        </a>
      )}
    </div>
  )
}

/**
 * TechStackGraph — interactive D3 force-directed graph showing how a project's
 * technologies relate to each other.
 *
 * HOW IT WORKS:
 * 1. Each technology becomes a circular SVG node (group 1). The project itself
 *    is the central node (group 0, pinned at the canvas centre with fx/fy).
 * 2. D3 simulates physical forces (attraction via links, repulsion via charge,
 *    collision avoidance) until nodes settle into a stable layout.
 * 3. Hover → transient tooltip. Click node → pinned tooltip (stays until the
 *    user clicks the node again or clicks the SVG background).
 * 4. The `activeTag` prop dims nodes that don't belong to the active category
 *    by transitioning their SVG opacity to 0.2.
 * 5. "Expand View" button increases link distance and repulsion, spreading
 *    nodes further apart without rebuilding the graph.
 *
 * IMPORTANT: All D3 mutations happen *outside* React's virtual DOM — we only
 * touch the raw SVG element via the `svgRef`. React state is used only for
 * tooltip visibility and the expand toggle. This avoids reconciliation
 * conflicts between React and D3.
 */
const TechStackGraph: React.FC<TechStackGraphProps> = ({ project, activeTag }) => {
  const svgRef = useRef<SVGSVGElement>(null)
  const simulationRef = useRef<d3.Simulation<NodeData, LinkData> | null>(null)
  const [tooltipData, setTooltipData] = useState<{
    data: NodeData
    position: { top: number; left: number }
    pinned: boolean
  } | null>(null)
  const [isExpanded, setIsExpanded] = useState(false)
  // tooltipDataRef mirrors tooltipData in a ref so D3 event handlers can read
  // the latest value without being recreated every render (stale closure fix).
  const tooltipDataRef = useRef<typeof tooltipData>(null)

  // Keep the ref in sync with state so D3 event callbacks always see the
  // current tooltip state without needing to close over it.
  useEffect(() => {
    tooltipDataRef.current = tooltipData
  }, [tooltipData])

  // ── Main graph construction ────────────────────────────────────────────────
  // Runs whenever `project` changes (i.e. when the parent selects a different
  // project). Tears down the previous SVG, rebuilds nodes/links, and starts a
  // fresh D3 simulation.
  useEffect(() => {
    if (!svgRef.current) return
    const container = svgRef.current.parentElement
    if (!container) return

    const width = container.clientWidth
    const height = 400

    // group 0 = central project node (pinned via fx/fy so it never drifts)
    // group 1 = technology satellite nodes (free to be pulled by forces)
    const nodes: NodeData[] = [
      { id: project.name, group: 0, radius: 25, fx: width / 2, fy: height / 2 },
      ...project.technologies.map(tech => ({ id: tech, group: 1, radius: 15 })),
    ]
    // Each tech links back to the project hub — star topology radiating out
    const links: (Omit<LinkData, 'source' | 'target'> & {
      source: string
      target: string
    })[] = project.technologies.map(tech => ({
      source: tech,
      target: project.name,
    }))

    const svg = d3
      .select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height])
    svg.selectAll('*').remove()

    svg.on('click', () => {
      if (tooltipDataRef.current?.pinned) setTooltipData(null)
    })

    const linkForce = d3.forceLink<NodeData, LinkData>(links).id(d => d.id)

    simulationRef.current = d3
      .forceSimulation(nodes)
      .force('link', linkForce)
      .force('charge', d3.forceManyBody())
      .force('collide', d3.forceCollide<NodeData>().radius(d => d.radius + 5))
      .force('center', d3.forceCenter(width / 2, height / 2))

    const link = svg
      .append('g')
      .attr('stroke-opacity', 0.6)
      .selectAll('line')
      .data(linkForce.links())
      .join('line')
      .attr('class', 'link')

    const node = svg
      .append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .attr('class', 'node-group')
      .call(drag(simulationRef.current))
    node.append('circle').attr('r', d => d.radius)
    node
      .append('text')
      .text(d => d.id)
      .attr('text-anchor', 'middle')
      .attr('dy', '0.3em')
      .style('font-size', d => (d.group === 0 ? '12px' : '10px'))
      .style('pointer-events', 'none')
      .style('font-weight', d => (d.group === 0 ? 'bold' : 'normal'))

    node
      .on('mouseover', (event, d) => {
        if (d.group !== 0 && !tooltipDataRef.current?.pinned) {
          setTooltipData({
            data: d,
            position: { top: event.clientY, left: event.clientX },
            pinned: false,
          })
        }
      })
      .on('mouseout', () => {
        if (!tooltipDataRef.current?.pinned) setTooltipData(null)
      })
      .on('click', (event, d) => {
        event.stopPropagation()
        if (d.group !== 0) {
          if (tooltipDataRef.current?.pinned && tooltipDataRef.current.data.id === d.id) {
            setTooltipData(null)
          } else {
            setTooltipData({
              data: d,
              position: { top: event.clientY, left: event.clientX },
              pinned: true,
            })
          }
        }
      })

    simulationRef.current.on('tick', () => {
      link
        .attr('x1', d => (d.source as NodeData).x!)
        .attr('y1', d => (d.source as NodeData).y!)
        .attr('x2', d => (d.target as NodeData).x!)
        .attr('y2', d => (d.target as NodeData).y!)
      node.attr('transform', d => `translate(${d.x}, ${d.y})`)
    })

    function drag(simulation: d3.Simulation<NodeData, any>) {
      return d3
        .drag<any, NodeData>()
        .on('start', event => {
          if (!event.active) simulation.alphaTarget(0.3).restart()
          event.subject.fx = event.subject.x
          event.subject.fy = event.subject.y
          setTooltipData(null)
          const dragTarget = event.sourceEvent?.target?.parentNode
          if (dragTarget) {
            d3.select(dragTarget).classed('dragging', true)
          }
        })
        .on('drag', event => {
          event.subject.fx = event.x
          event.subject.fy = event.y
        })
        .on('end', event => {
          if (!event.active) simulation.alphaTarget(0)
          event.subject.fx = null
          event.subject.fy = null
          const dragTarget = event.sourceEvent?.target?.parentNode
          if (dragTarget) {
            d3.select(dragTarget).classed('dragging', false)
          }
        })
    }

    // Cleanup: detach the SVG click handler and stop the physics simulation so
    // it doesn't keep running in the background after a project switch.
    return () => {
      svg.on('click', null)
      simulationRef.current?.stop()
    }
  }, [project])

  // ── Expand / collapse layout ───────────────────────────────────────────────
  // Instead of rebuilding the graph, we just update the force parameters and
  // "heat" the simulation with alpha(1) so it re-settles at the new distances.
  useEffect(() => {
    if (!simulationRef.current) return
    const linkDistance = isExpanded ? 180 : 120
    const chargeStrength = isExpanded ? -300 : -200

    ;(simulationRef.current.force('link') as d3.ForceLink<NodeData, LinkData>).distance(
      linkDistance,
    )
    ;(simulationRef.current.force('charge') as d3.ForceManyBody<NodeData>).strength(
      chargeStrength,
    )
    simulationRef.current.alpha(1).restart()
  }, [isExpanded, project])

  // ── Tag-based filtering ────────────────────────────────────────────────────
  // When the parent passes a new `activeTag` (e.g. 'frontend'), every node
  // whose TECHNOLOGY_TAGS entry does NOT include that tag fades to 0.2 opacity.
  // The project hub node (group 0) is always fully visible.
  // If activeTag is null (no filter active), all nodes are fully opaque.
  useEffect(() => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    svg
      .selectAll<SVGGElement, NodeData>('.node-group')
      .transition()
      .duration(300)
      .style('opacity', d =>
        !activeTag || d.group === 0 || (TECHNOLOGY_TAGS[d.id] || []).includes(activeTag)
          ? 1
          : 0.2,
      )
  }, [activeTag, project])

  // ── Tooltip-driven node/link highlighting ─────────────────────────────────
  // When a node is hovered or pinned, we apply the 'highlighted' CSS class to
  // that node's group and to any link that connects to it.
  // D3's .classed() is more efficient than re-rendering React for SVG mutations.
  useEffect(() => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    const highlightedNodeId = tooltipData?.data.id
    svg
      .selectAll('.node-group')
      .classed('highlighted', d => (d as NodeData).id === highlightedNodeId)
    svg.selectAll('.link').classed('highlighted', l => {
      // After simulation runs, D3 replaces string source/target with actual
      // node objects. We handle both forms to avoid type errors.
      const sourceId = typeof (l as any).source === 'object' ? (l as any).source.id : (l as any).source
      const targetId = typeof (l as any).target === 'object' ? (l as any).target.id : (l as any).target
      return sourceId === highlightedNodeId || targetId === highlightedNodeId
    })
  }, [tooltipData, project])

  return (
    <div className="relative w-full flex flex-col justify-center items-center bg-gray-800/50 rounded-lg p-4 my-4">
      <style>{`
                .node-group circle {
                    fill: #374151; stroke: #4A5568; stroke-width: 2px;
                    transition: filter 0.2s ease-out, transform 0.2s ease-out;
                }
                .node-group:first-child circle { fill: #2DD4BF; stroke: #14B8A6; }
                .node-group text { fill: white; }
                .link { stroke: #4A5568; transition: all 0.2s ease-out; }
                .node-group.dragging circle, .node-group.highlighted circle {
                    filter: drop-shadow(0 0 8px #2dd4bf);
                    stroke: #2dd4bf;
                    transform: scale(1.1);
                }
                .link.highlighted { stroke: #2dd4bf; stroke-width: 2px; }
            `}</style>
      <div className="absolute top-2 right-2 z-10">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="px-3 py-1 text-xs font-medium bg-gray-700 text-cyan-200 rounded-md hover:bg-gray-600 transition-colors"
        >
          {isExpanded ? 'Collapse View' : 'Expand View'}
        </button>
      </div>
      <svg ref={svgRef}></svg>
      <Tooltip tooltipData={tooltipData} />
    </div>
  )
}

export default TechStackGraph
