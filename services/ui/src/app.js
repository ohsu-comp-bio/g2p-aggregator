import React, { Component } from "react";
import { render } from "react-dom";
import elasticsearch from "elasticsearch";

import ReactJson from 'react-json-view'

import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import SearchBar from 'material-ui-search-bar'

import ReactTable from "react-table";
import reactTableStyles from "react-table/react-table.css";
//includes styles for table
import "./index.css";

import AutoComplete from 'material-ui/AutoComplete';
import AppBar from 'material-ui/AppBar';
import Chip from 'material-ui/Chip';
import {blue300, indigo900} from 'material-ui/styles/colors';
import FontIcon from 'material-ui/FontIcon';
import Avatar from 'material-ui/Avatar';

const config = require('./config.json');

let client = new elasticsearch.Client({
  host: config.host,
  log: config.log
});


const styles = {
  chip: {
    margin: 4,
  },
  wrapper: {
    display: 'flex',
    flexWrap: 'wrap',
  },
};


class App extends Component {
  // main app
  constructor(props) {
    super(props);

    this.state = {
      results: [],
      suggestions: [],
      pages: -1,
      loading: false,
      sample_queries: [
        {id:'no_trials',  q:'-source:*trials'},
        {id:'all_trials', q:'+source:*trials'},
        {id:'oncogenic',  q:'-association.environmentalContexts:*'},
        {id:'predictive', q:'+association.environmentalContexts:*'},
      ]
     };
  }
  //
  handleChange(event) {

    this.setState({
      suggestions: [],
      current_query: event
    });

  }
  // search bar callbacks
  handleClear() {
    this.setState({
      suggestions: [],
    });
  }
  handleSearch() {
    this.setState({
      search_query: this.state.current_query
    });
  }
  //
  handleChipClick(sample_query_id) {
    const sample_queries = this.state.sample_queries;
    const sample_query_idx = sample_queries.map((q) => q.id).indexOf(sample_query_id);
    sample_queries[sample_query_idx].checked = !sample_queries[sample_query_idx].checked
    let current_query = this.state.current_query ;
    if (sample_queries[sample_query_idx].checked) {
      current_query = this.state.current_query + ' ' + this.state.sample_queries[sample_query_idx].q;
    } else {
      current_query = current_query.replace(this.state.sample_queries[sample_query_idx].q, '');
    }
    this.setState({
      current_query: current_query,
      sample_queries: sample_queries
      },
      () => this.handleSearch()
    );
  }

  //
  renderChip(sample_query) {
    let avatar = null;
    if (sample_query.checked) {
      avatar = <Avatar icon={<FontIcon className="material-icons">done</FontIcon>} />
    }
    return (
      <Chip
        key={sample_query.id}
        onClick={() => this.handleChipClick(sample_query.id)}
        style={styles.chip}
      >
        {avatar}
        {sample_query.id}
      </Chip>
    );
  }


  //
  render() {
  //

    return (
      <MuiThemeProvider>
        <div id="container">
          <AppBar
            title="VICC"
            onLeftIconButtonClick={e => (alert('Alpha G2P browser'))}
          >
          </AppBar>
          <SearchBar
            value={this.state.current_query}
            autoFocus
            hintText="Start typing a gene, variant name, drug or disease.  e.g. MDM4, Breast, Ponatinib, ..."
            onChange={e => this.handleChange(e)}
            onRequestSearch={e => this.handleSearch(e)}
          />
          <div style={styles.wrapper}>
            {this.state.sample_queries.map(this.renderChip, this)}
          </div>
          <ReactTable
            key={this.state.search_query}
            pages={this.state.pages}
            loading={this.state.loading}
            styles={reactTableStyles}
            data={this.state.results}
            filterable
            manual
            columns={[
              {
                Header: "",
                headerClassName: 'alternate-header-group',
                columns: [
                  {
                    Header: "source",
                    accessor: "_source.source",
                    Filter: ({filter, onChange}) => (
                      <ColumnFilter  accessor={"_source.source"}
                                     onChange={onChange} currentQuery={() => (this.state.current_query)} />
                    ),
                    Cell: (row) => {
                			return <ReactJson src={row.original._source}
                        indentWidth={2}
                        displayDataTypes={false}
                        collapsed={true}
                        name={row.original._source.source}
                        displayObjectSize={false}/>
                    }
                  }
                ]
              },
              {
                Header: "Genotype",
                columns: [
                  {
                    Header: "genes",
                    accessor: "_source.genes",
                    Filter: ({filter, onChange}) => (
                      <ColumnFilter  accessor={"_source.genes"}
                                     onChange={onChange} currentQuery={() => (this.state.current_query)} />
                    ),
                    Cell: (row) => {
                      const genes = row.original._source.genes.map(x=>x).join(", ")
                      return <ReactJson src={row.original._source.genes}
                        indentWidth={2}
                        displayDataTypes={false}
                        collapsed={true}
                        name={genes}
                        displayObjectSize={false}/>
                    }
                  },
                  {
                    Header: "features",
                    accessor: "_source.features.description",
                    Filter: ({filter, onChange}) => (
                      <ColumnFilter  accessor={"_source.features.description"}
                                     onChange={onChange} currentQuery={() => (this.state.current_query)} />
                    ),
                    Cell: (row) => {
                      if (row.original._source.features.length == 0) {
                        return <span/>
                      }

                      const descriptions = row.original._source.features
                                            .map(f=>f.description || f.name)
                                            .filter(d=>d!=undefined)
                                            .join(", ");
                      return <ReactJson src={row.original._source.features}
                        indentWidth={2}
                        displayDataTypes={false}
                        collapsed={true}
                        name={descriptions}
                        displayObjectSize={false}/>
                    }
                  },
                  {
                    Header: "synonyms",
                    accessor: "_source.features.synonyms",
                    sortable: false,
                    Filter: ({filter, onChange}) => (
                      <ColumnFilter  accessor={"_source.features.synonyms"}
                                     onChange={onChange} currentQuery={() => (this.state.current_query)} />
                    ),
                    Cell: (row) => {
                      const synonyms = row.original._source.features
                                        .filter(f=>f.synonyms)
                                        .map(f=>f.synonyms)
                                        .map(s=>s)
                      const synonym_names =  synonyms.join(", ")
                      if (synonyms.length == 0) {
                        return <span/>
                      }
                      return <ReactJson src={synonyms}
                        indentWidth={2}
                        displayDataTypes={false}
                        collapsed={true}
                        name={synonym_names}
                        displayObjectSize={false}/>
                    }
                  },
                ]
              },
              {
                Header: "Phenotype",
                headerClassName: 'alternate-header-group',
                columns: [
                  {
                    Header: "family",
                    accessor: "_source.association.phenotype.family",
                    Filter: ({filter, onChange}) => (
                      <ColumnFilter  accessor={"_source.association.phenotype.family"}
                                     onChange={onChange} currentQuery={() => (this.state.current_query)} />
                    ),
                    Cell: (row) => {
                      return <span>{row.original._source.association.phenotype.family}</span>
                    }
                  },
                  {
                    Header: "condition",
                    accessor: "_source.association.phenotype.description",
                    Filter: ({filter, onChange}) => (
                      <ColumnFilter  accessor={"_source.association.phenotype.description"}
                                     onChange={onChange} currentQuery={() => (this.state.current_query)} />
                    ),
                    Cell: (row) => {
                      return <ReactJson src={row.original._source.association.phenotype}
                          indentWidth={2}
                          displayDataTypes={false}
                          collapsed={true}
                          name={row.original._source.association.phenotype.description}
                          displayObjectSize={false}/>
                    }
                  }
                ]
              },
              {
                Header: "Environment",
                columns: [
                  {
                    Header: "description",
                    accessor: "_source.association.environmentalContexts.description",
                    Filter: ({filter, onChange}) => (
                      <ColumnFilter  accessor={"_source.association.environmentalContexts.description"}
                                     onChange={onChange} currentQuery={() => (this.state.current_query)} />
                    ),
                    Cell: (row) => {
                      const environmentalContexts = row.original._source.association.environmentalContexts;
                      if (!environmentalContexts || environmentalContexts.length == 0) {
                        return <span/>
                      }
                      const descriptions = environmentalContexts
                                        .map(e=>e.description)
                                        .join(', ')

                      return <ReactJson src={environmentalContexts}
                          indentWidth={2}
                          displayDataTypes={false}
                          collapsed={true}
                          name={descriptions}
                          displayObjectSize={false}/>
                    }
                  }
                ]
              },
              {
                Header: "Evidence",
                headerClassName: 'alternate-header-group',
                columns: [
                  {
                    Header: "amp guideline",
                    accessor: "_source.association.evidence_label",
                    Filter: ({filter, onChange}) => (
                      <ColumnFilter  accessor={"_source.association.evidence_label"}
                                     onChange={onChange} currentQuery={() => (this.state.current_query)} />
                    ),
                    Cell: (row) => {
                      return <span>{row.original._source.association.evidence_label}</span>
                    }
                  },
                  {
                    Header: "description",
                    accessor: "_source.association.evidence.description",
                    Filter: ({filter, onChange}) => (
                      <ColumnFilter  accessor={"_source.association.evidence.description"}
                                     onChange={onChange} currentQuery={() => (this.state.current_query)} />
                    ),
                    Cell: (row) => {
                      if (row.original._source.association.evidence.length == 0) {
                        return <span/>
                      }
                      return <span>{row.original._source.association.evidence[0].description}</span>
                    }
                  },
                  {
                    Header: "publications",
                    accessor: "_source.association.evidence.info.publications",
                    Filter: ({filter, onChange}) => (
                      <ColumnFilter  accessor={"_source.association.evidence.info.publications"}
                                     onChange={onChange} currentQuery={() => (this.state.current_query)} />
                    ),
                    Cell: (row) => {
                      const evidence = row.original._source.association.evidence;
                      if (evidence.length == 0) {
                        return <span/>
                      }
                      const publications = evidence.map(e=> e.info ? e.info.publications : []).map(p=>p)
                      const links = publications.map(p=>(<a key={p} href={p} target="_blank" >{p}</a>))
                      return <span>{links}</span>
                    }
                  }

                ]
              }
            ]}
            defaultPageSize={10}
            className="-striped -highlight"
            onFetchData={(state, instance) => {
              // ***** control all fetching of data
              // console.log({ page: state.page, pageSize: state.pageSize, sorted: state.sorted, filtered: state.filtered, search_query: this.state.search_query, });
              // show the loading overlay
              this.setState({loading: true})
              // determine sort order
              const sorted = state.sorted
                .map(s => {
                  var d = 'asc'
                  if (s.desc) {
                    d = 'desc'
                  }
                  return s.id.replace('_source.','') + '.keyword' + ':' + d ;
                } )
                .join(', ')
              // determine query
              var  q = this.state.search_query || ''
              const filtered = state.filtered
                .map(f => {
                  return f.id.replace('_source.','+') + ":\"" + f.value  +"\"";
                  } )
                .join(' ')
              if (filtered.length > 0) {
                q = q + ' ' + filtered
              }

              q = q || '*'
              this.setState({current_query: q})
              // fetch your data
              client
                .search({
                  q: q ,
                  index: 'associations',
                  from: state.pageSize * state.page,
                  sort: sorted,
                  size: state.pageSize
                })
                .then(
                  function(body) {
                    this.setState({
                      results: body.hits.hits,
                      pages: Math.ceil(body.hits.total / state.pageSize),
                      loading: false
                    });
                  }.bind(this),
                  function(error) {
                    console.trace(error.message);
                    this.setState({loading:false})
                    alert(error.message);
                  }.bind(this)
                );
            }}
          />
        </div>
      </MuiThemeProvider>
    );
  }
}

class ColumnFilter extends Component {
  // auto complete
  constructor(props) {
    super(props);
    this.state = {
      dataSource: []
    };
    // initialize dropdown
    this.initialized = false;
  }

  handleUpdateInput(value) {
    const field = this.props.accessor.replace('_source.','') + '.keyword';
    const currentQuery = this.props.currentQuery;
    //prep query
    function hasRestrictedCharacters(src, restricted) {
      const matches = restricted.split('').filter(r => src.includes(r))
      return matches.length > 0
    }
    // default is the current query scope
    var q = currentQuery()
    // escape and exact match if funny characters
    if (value && hasRestrictedCharacters(value, '+-&&||!(){}[]^"~*?:\\') ) {
      q = q + ' +' + field + ":\"" + value + "\""
    } else if (value) {
      // otherwise wildcards
      q = q + ' +' + field + ':' + value + '*'
    }
    //run it
    client
      .search({
        index: 'associations',
        body: {
            size: 0 ,
            query: {
              query_string: {
                query: q,
                analyze_wildcard: true
              }
            },
            aggs: {
              values: {
                  terms: {
                      field: field,
                      size: 10,
                      order: {
                        _count: 'desc'
                      },
                      include:  value ? value + '.*' : value
                  }
              }
            }
        }
      })
      .then(
        function(body) {
          //set choices
          this.setState({
            dataSource: body.aggregations.values.buckets.map(b=>b.key),
          });
        }.bind(this),
        function(error) {
          console.trace(error.message);
          alert(error.message);
        }.bind(this)
      );
  };

  initIfNecessary() {
    if (this.state.dataSource.length==0 && !this.initialized){
      //prevent loops
      this.initialized = true;
      this.handleUpdateInput();
    }
  }

  render() {
    const onChange = this.props.onChange;
    // see http://www.material-ui.com/#/components/auto-complete
    // https://github.com/mui-org/material-ui/issues/3630#issuecomment-226003483
    return (

      <AutoComplete
        id={this.props.accessor}
        style={{
          width: '100%',
        }}
        openOnFocus={true}
        animated={true}
        dataSource={this.state.dataSource}
        filter={(searchText: string, key: string) => true}
        onUpdateInput={e => this.handleUpdateInput(e)}
        onFocus={e => this.initIfNecessary(e)}
        onNewRequest={(chosenRequest,index) => onChange(chosenRequest)}
      />
    );
  }
}




render(<App />, document.getElementById("main"));
