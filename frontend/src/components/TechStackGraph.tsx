import React, { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'

export interface Project {
  name: string
  technologies: string[]
}

export const TECH_PURPOSES: Record<string, string> = {}
export const TECHNOLOGY_TAGS: Record<string, string[]> = {}

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

const TechStackGraph: React.FC<TechStackGraphProps> = ({ project, activeTag }) => {
  const svgRef = useRef<SVGSVGElement>(null)
  const simulationRef = useRef<d3.Simulation<NodeData, LinkData> | null>(null)
  const [tooltipData, setTooltipData] = useState<{
    data: NodeData
    position: { top: number; left: number }
    pinned: boolean
  } | null>(null)
  const [isExpanded, setIsExpanded] = useState(false)
  const tooltipDataRef = useRef<typeof tooltipData>(null)

  useEffect(() => {
    tooltipDataRef.current = tooltipData
  }, [tooltipData])

  useEffect(() => {
    if (!svgRef.current) return
    const container = svgRef.current.parentElement
    if (!container) return

    const width = container.clientWidth
    const height = 400

    const nodes: NodeData[] = [
      { id: project.name, group: 0, radius: 25, fx: width / 2, fy: height / 2 },
      ...project.technologies.map(tech => ({ id: tech, group: 1, radius: 15 })),
    ]
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

    return () => {
      svg.on('click', null)
      simulationRef.current?.stop()
    }
  }, [project])

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

  useEffect(() => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    const highlightedNodeId = tooltipData?.data.id
    svg
      .selectAll('.node-group')
      .classed('highlighted', d => (d as NodeData).id === highlightedNodeId)
    svg.selectAll('.link').classed('highlighted', l => {
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
