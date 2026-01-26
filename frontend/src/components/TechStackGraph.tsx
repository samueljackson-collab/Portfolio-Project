import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';
import type { Project } from '../types';
import { TECH_PURPOSES, TECHNOLOGY_TAGS } from '../constants';

interface TechStackGraphProps {
  project: Project;
  activeTag: string | null;
}

interface NodeData extends d3.SimulationNodeDatum {
  id: string;
  group: number;
  radius: number;
  isCenter: boolean;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

interface LinkData extends d3.SimulationLinkDatum<NodeData> {}

interface TooltipState {
  data: NodeData;
  position: { top: number; left: number };
  pinned: boolean;
}

const Tooltip: React.FC<{ tooltipData: TooltipState | null }> = ({ tooltipData }) => {
  if (!tooltipData) return null;

  const purpose =
    TECH_PURPOSES[tooltipData.data.id] ||
    (tooltipData.data.group === 0 ? 'Project Hub' : 'Core technology');
  const learnMoreLink = `https://www.google.com/search?q=${encodeURIComponent(tooltipData.data.id)}+documentation`;

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
  );
};

const TechStackGraph: React.FC<TechStackGraphProps> = ({ project, activeTag }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<NodeData, LinkData> | null>(null);
  const tooltipRef = useRef<TooltipState | null>(null);
  const [tooltipData, setTooltipData] = useState<TooltipState | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  // Keep ref in sync with state to avoid stale closures in D3 event handlers
  useEffect(() => {
    tooltipRef.current = tooltipData;
  }, [tooltipData]);

  // Memoized tooltip setter that uses ref for current state
  const updateTooltip = useCallback((newData: TooltipState | null) => {
    setTooltipData(newData);
  }, []);

  // Main D3 setup effect - only depends on project, NOT tooltipData
  useEffect(() => {
    if (!svgRef.current) return;
    const container = svgRef.current.parentElement;
    if (!container) return;

    const width = container.clientWidth;
    const height = 400;

    const nodes: NodeData[] = [
      { id: project.name, group: 0, radius: 25, isCenter: true, fx: width / 2, fy: height / 2 },
      ...project.technologies.map((tech) => ({
        id: tech,
        group: 1,
        radius: 15,
        isCenter: false,
      })),
    ];
    const links: Array<{ source: string; target: string }> = project.technologies.map((tech) => ({
      source: tech,
      target: project.name,
    }));

    const svg = d3
      .select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height]);
    svg.selectAll('*').remove();

    // Handle click on SVG background to dismiss pinned tooltip
    const handleSvgClick = () => {
      if (tooltipRef.current?.pinned) {
        updateTooltip(null);
      }
    };
    svg.on('click', handleSvgClick);

    const linkForce = d3.forceLink<NodeData, LinkData>(links as unknown as LinkData[]).id((d) => d.id);

    simulationRef.current = d3
      .forceSimulation(nodes)
      .force('link', linkForce)
      .force('charge', d3.forceManyBody().strength(-200))
      .force(
        'collide',
        d3.forceCollide<NodeData>().radius((d) => d.radius + 5)
      )
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append('g')
      .attr('stroke-opacity', 0.6)
      .selectAll('line')
      .data(linkForce.links())
      .join('line')
      .attr('class', 'link');

    const node = svg
      .append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .attr('class', (d) => `node-group ${d.isCenter ? 'center-node' : ''}`)
      .call(drag(simulationRef.current));

    node.append('circle').attr('r', (d) => d.radius);
    node
      .append('text')
      .text((d) => d.id)
      .attr('text-anchor', 'middle')
      .attr('dy', '0.3em')
      .style('font-size', (d) => (d.group === 0 ? '12px' : '10px'))
      .style('pointer-events', 'none')
      .style('font-weight', (d) => (d.group === 0 ? 'bold' : 'normal'));

    node
      .on('mouseover', (event, d) => {
        if (d.group !== 0 && !tooltipRef.current?.pinned) {
          updateTooltip({
            data: d,
            position: { top: event.clientY, left: event.clientX },
            pinned: false,
          });
        }
      })
      .on('mouseout', () => {
        if (!tooltipRef.current?.pinned) {
          updateTooltip(null);
        }
      })
      .on('click', (event, d) => {
        event.stopPropagation();
        if (d.group !== 0) {
          const currentTooltip = tooltipRef.current;
          if (currentTooltip?.pinned && currentTooltip.data.id === d.id) {
            updateTooltip(null);
          } else {
            updateTooltip({
              data: d,
              position: { top: event.clientY, left: event.clientX },
              pinned: true,
            });
          }
        }
      });

    simulationRef.current.on('tick', () => {
      link
        .attr('x1', (d) => (d.source as NodeData).x ?? 0)
        .attr('y1', (d) => (d.source as NodeData).y ?? 0)
        .attr('x2', (d) => (d.target as NodeData).x ?? 0)
        .attr('y2', (d) => (d.target as NodeData).y ?? 0);
      node.attr('transform', (d) => `translate(${d.x ?? 0}, ${d.y ?? 0})`);
    });

    function drag(simulation: d3.Simulation<NodeData, LinkData>) {
      return d3
        .drag<SVGGElement, NodeData>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
          updateTooltip(null);

          const parentNode = event.sourceEvent?.target?.parentNode;
          if (parentNode) {
            d3.select(parentNode).classed('dragging', true);
          }
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);

          // Only release non-center nodes; center node stays fixed
          if (!d.isCenter) {
            d.fx = null;
            d.fy = null;
          }

          const parentNode = event.sourceEvent?.target?.parentNode;
          if (parentNode) {
            d3.select(parentNode).classed('dragging', false);
          }
        });
    }

    return () => {
      simulationRef.current?.stop();
      svg.on('click', null); // Clean up event listener
    };
  }, [project, updateTooltip]);

  // Handle expand/collapse view
  useEffect(() => {
    if (!simulationRef.current) return;
    const linkDistance = isExpanded ? 180 : 120;
    const chargeStrength = isExpanded ? -300 : -200;

    const linkForce = simulationRef.current.force('link') as d3.ForceLink<NodeData, LinkData> | undefined;
    const chargeForce = simulationRef.current.force('charge') as d3.ForceManyBody<NodeData> | undefined;

    if (linkForce) linkForce.distance(linkDistance);
    if (chargeForce) chargeForce.strength(chargeStrength);

    simulationRef.current.alpha(1).restart();
  }, [isExpanded]);

  // Handle active tag filtering
  useEffect(() => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    svg
      .selectAll<SVGGElement, NodeData>('.node-group')
      .transition()
      .duration(300)
      .style('opacity', (d) =>
        !activeTag || d.group === 0 || (TECHNOLOGY_TAGS[d.id] || []).includes(activeTag) ? 1 : 0.2
      );
  }, [activeTag]);

  // Handle highlighting based on tooltip
  useEffect(() => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    const highlightedNodeId = tooltipData?.data.id;

    svg.selectAll<SVGGElement, NodeData>('.node-group').classed('highlighted', (d) => d.id === highlightedNodeId);

    svg.selectAll<SVGLineElement, LinkData>('.link').classed('highlighted', (l) => {
      const source = l.source as NodeData;
      const target = l.target as NodeData;
      const sourceId = typeof source === 'object' ? source.id : source;
      const targetId = typeof target === 'object' ? target.id : target;
      return sourceId === highlightedNodeId || targetId === highlightedNodeId;
    });
  }, [tooltipData]);

  return (
    <div className="relative w-full flex flex-col justify-center items-center bg-gray-800/50 rounded-lg p-4 my-4">
      <style>{`
        .node-group circle {
          fill: #374151;
          stroke: #4A5568;
          stroke-width: 2px;
          transition: filter 0.2s ease-out, transform 0.2s ease-out;
        }
        .node-group.center-node circle {
          fill: #2DD4BF;
          stroke: #14B8A6;
        }
        .node-group text {
          fill: white;
        }
        .link {
          stroke: #4A5568;
          transition: all 0.2s ease-out;
        }
        .node-group.dragging circle,
        .node-group.highlighted circle {
          filter: drop-shadow(0 0 8px #2dd4bf);
          stroke: #2dd4bf;
          transform: scale(1.1);
        }
        .link.highlighted {
          stroke: #2dd4bf;
          stroke-width: 2px;
        }
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
  );
};

export default TechStackGraph;
