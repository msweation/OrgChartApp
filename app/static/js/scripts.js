document.getElementById('file-input').addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('file', file);
        fetch('/upload', {
            method: 'POST',
            body: formData
        }).then(response => response.json()).then(data => {
            renderChart(data);
        });
    }
});

function renderChart(data) {
    const width = document.getElementById('chart').clientWidth;
    const height = document.getElementById('chart').clientHeight;
    const svg = d3.select('#chart').append('svg')
        .attr('width', width)
        .attr('height', height);

    const root = d3.hierarchy(data[0]);
    const treeLayout = d3.tree().size([width, height]);
    treeLayout(root);

    svg.selectAll('line')
        .data(root.links())
        .enter()
        .append('line')
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)
        .attr('stroke', '#ccc');

    svg.selectAll('circle')
        .data(root.descendants())
        .enter()
        .append('circle')
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)
        .attr('r', 5)
        .attr('fill', '#69b3a2');

    svg.selectAll('text')
        .data(root.descendants())
        .enter()
        .append('text')
        .attr('x', d => d.x)
        .attr('y', d => d.y - 10)
        .attr('text-anchor', 'middle')
        .text(d => d.data.name);
}

document.getElementById('search-bar').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    const nodes = d3.selectAll('text').filter(d => d.data.name.toLowerCase().includes(searchTerm));
    
    d3.selectAll('text').attr('fill', '#000');
    d3.selectAll('circle').attr('fill', '#69b3a2');

    if (searchTerm) {
        nodes.attr('fill', 'red');
        nodes.each(function(d) {
            d3.select(`circle[cx="${d.x}"][cy="${d.y}"]`).attr('fill', 'red');
        });
    }
});
