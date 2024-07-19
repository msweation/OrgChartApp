let currentSearch;

document.getElementById('search-button').addEventListener('click', () => {
    updateChart();
});

document.getElementById('search-bar').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        updateChart();
    }
});

document.getElementById('toggle-inactive').addEventListener('change', () => {
    const searchTerm = document.getElementById('search-bar').value.toLowerCase();

    if (searchTerm !== currentSearch) {
        return;
    }
    updateChart();
});

window.addEventListener('popstate', (event) => {
    if (event.state && event.state.searchTerm) {
        document.getElementById('search-bar').value = event.state.searchTerm;
        const showInactive = document.getElementById('toggle-inactive').checked;
        fetch(`/get_org_chart?search=${event.state.searchTerm}&showInactive=${showInactive}`)
            .then(response => response.json())
            .then(data => {
                if (!data) {
                    alert('No data found');
                    return;
                }
                renderChart(data);
            })
            .catch(error => {
                console.error('Error fetching org chart data:', error);
                alert('An error occurred while fetching the data.');
            });
    }
});

function updateChart() {
    const searchTerm = document.getElementById('search-bar').value.toLowerCase();
    currentSearch = searchTerm;
    const showInactive = document.getElementById('toggle-inactive').checked;

    // Update the URL
    const newUrl = `/search/${searchTerm.replace(/\s+/g, '-')}`;
    history.pushState({ searchTerm }, '', newUrl);

    // Fetch the org chart data with the current filters
    fetch(`/get_org_chart?search=${searchTerm}&showInactive=${showInactive}`)
        .then(response => response.json())
        .then(data => {
            if (!data) {
                alert('No data found');
                return;
            }
            renderChart(data);
        })
        .catch(error => {
            console.error('Error fetching org chart data:', error);
            alert('An error occurred while fetching the data.');
        });
}

function renderChart(data) {
    // Clear any existing chart
    console.log('Attempting to load chart for data: ', data);
    d3.select('#chart').html('');

    const width = document.getElementById('chart').clientWidth;
    const height = document.getElementById('chart').clientHeight;
    const padding = 10;

    const firstLevelChildren = data.children ? data.children.length : 0;

    const getNodeLevels = (node) => {
        if (!node.children || node.children.length === 0) {
            return 0;
        }
        const childLevels = node.children.map(getNodeLevels);
        return 1 + Math.max(...childLevels);
    };

    const totalLevels = getNodeLevels(data);

    console.log('Total node levels: ',totalLevels)

    const treeWidthAdjustment = (firstLevelChildren * 10) + 10;

    console.log(firstLevelChildren);

    const svg = d3.select('#chart').append('svg')
        .attr('width', width)
        .attr('height', height)
        .call(d3.zoom().on('zoom', (event) => {
            svg.attr('transform', event.transform);
        }))
        .append('g');

    const root = d3.hierarchy(data);

    const treeLayout = d3.tree().size([width + treeWidthAdjustment, height - padding]);
    treeLayout(root);

    svg.selectAll('line')
        .data(root.links())
        .enter()
        .append('line')
        .attr('x1', d => d.source.x - (treeWidthAdjustment / 2))
        .attr('y1', d => d.source.y + padding)
        .attr('x2', d => d.target.x - (treeWidthAdjustment / 2))
        .attr('y2', d => d.target.y + padding)
        .attr('stroke', '#ccc');

    const nodes = svg.selectAll('circle')
        .data(root.descendants())
        .enter()
        .append('circle')
        .attr('cx', d => d.x - (treeWidthAdjustment / 2))
        .attr('cy', d => d.y + padding)
        .attr('r', 5)
        .attr('fill', d => d.data.active ? '#69b3a2' : '#ff0000')
        .on('mouseover', function(event, d) {
            d3.select(this).attr('r', 10);
            d3.select(this).style('cursor','pointer')
            d3.select(`#text-${d.data.name.replace(/\s+/g, '-')}`).style('display', 'none');
            const info = `Name: ${d.data.name}<br>Active: ${d.data.active}<br>Total Sales: ${d.data.sales}`;
            d3.select('#tooltip')
                .style('left', `${event.pageX + 10}px`)
                .style('top', `${event.pageY + 10}px`)
                .style('display', 'inline-block')
                .html(info);
        })
        .on('mouseout', function(event, d) {
            d3.select(this).attr('r', 5);
            d3.select(`#text-${d.data.name.replace(/\s+/g, '-')}`).style('display', 'inline');
            d3.select('#tooltip').style('display', 'none');
        })
        .on('click', function(event, d) {
            document.getElementById('search-bar').value = d.data.name;
            const searchTerm = document.getElementById('search-bar').value.toLowerCase();

            if (searchTerm === currentSearch) {
                return;
            }
            updateChart(); // Trigger the search and update the chart
            d3.selectAll('#tooltip').style('display', 'none');
        });

    svg.selectAll('text')
        .data(root.descendants())
        .enter()
        .append('text')
        .attr('x', d => d.x - (treeWidthAdjustment / 2))
        .attr('y', d => d.y + 15 + padding)
        .attr('text-anchor', 'middle')
        .attr('font-size', 12)
        .attr('id', d => `text-${d.data.name.replace(/\s+/g, '-')}`)
        .attr('class', 'sale-num')
        .text(d => `${d.data.sales}`);
}

// Create a tooltip div element for showing node information on hover
d3.select('body').append('div')
    .attr('id', 'tooltip')
    .style('position', 'absolute')
    .style('padding', '10px')
    .style('background', 'rgba(0, 0, 0, 0.7)')
    .style('color', 'white')
    .style('border-radius', '5px')
    .style('display', 'none');
