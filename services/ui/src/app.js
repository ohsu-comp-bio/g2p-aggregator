import React, { Component } from "react";
import { render } from "react-dom";

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
      results: undefined,
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
  renderConfig() {
    if (this.state.config) {
      return (
        <div>
          {this.state.config.host.host}
        </div>
      );
    }
  }

  // load config from server
  componentWillMount() {
    let _this = this;
    fetch('config.json')
      .then(function(response) {
        response.json().then(function(data) {
                    _this.setState({results: [], config: data});
                    console.log('componentWillMount', data)
                });
        }
      );
  }

  //
  renderTable() {
    if (!this.state.config) {
      return
    }
    return (
      <ReactTable
        key={this.state.search_query}
        pages={this.state.pages}
        loading={this.state.config != undefined && this.state.loading}
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
                accessor: "source",
                Filter: ({filter, onChange}) => (
                  <ColumnFilter  accessor={"source"}
                                 onChange={onChange} config={this.state.config}
                                 currentQuery={() => (this.state.current_query)} />
                ),
                Cell: (row) => {
                  return <ReactJson src={row.original}
                    indentWidth={2}
                    displayDataTypes={false}
                    collapsed={true}
                    name={row.original.source}
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
                accessor: "genes",
                Filter: ({filter, onChange}) => (
                  <ColumnFilter  accessor={"genes"}
                                 onChange={onChange} config={this.state.config} currentQuery={() => (this.state.current_query)} />
                ),
                Cell: (row) => {
                  const genes = row.original.genes.map(x=>x).join(", ")
                  return <ReactJson src={row.original.genes}
                    indentWidth={2}
                    displayDataTypes={false}
                    collapsed={true}
                    name={genes}
                    displayObjectSize={false}/>
                }
              },
              {
                Header: "features",
                accessor: "features.description",
                Filter: ({filter, onChange}) => (
                  <ColumnFilter  accessor={"features.description"}
                                 onChange={onChange} config={this.state.config} currentQuery={() => (this.state.current_query)} />
                ),
                Cell: (row) => {
                  if (row.original.features.length == 0) {
                    return <span/>
                  }

                  const descriptions = row.original.features
                                        .map(f=>f.description || f.name)
                                        .filter(d=>d!=undefined)
                                        .join(", ");
                  return <ReactJson src={row.original.features}
                    indentWidth={2}
                    displayDataTypes={false}
                    collapsed={true}
                    name={descriptions}
                    displayObjectSize={false}/>
                }
              },
              {
                Header: "synonyms",
                accessor: "features.synonyms",
                sortable: false,
                Filter: ({filter, onChange}) => (
                  <ColumnFilter  accessor={"features.synonyms"}
                                 onChange={onChange} config={this.state.config} currentQuery={() => (this.state.current_query)} />
                ),
                Cell: (row) => {
                  const synonyms = row.original.features
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
                accessor: "association.phenotype.family",
                Filter: ({filter, onChange}) => (
                  <ColumnFilter  accessor={"association.phenotype.family"}
                                 onChange={onChange} config={this.state.config} currentQuery={() => (this.state.current_query)} />
                ),
                Cell: (row) => {
                  return <span>{row.original.association.phenotype.family}</span>
                }
              },
              {
                Header: "condition",
                accessor: "association.phenotype.description",
                Filter: ({filter, onChange}) => (
                  <ColumnFilter  accessor={"association.phenotype.description"}
                                 onChange={onChange} config={this.state.config} currentQuery={() => (this.state.current_query)} />
                ),
                Cell: (row) => {
                  return <ReactJson src={row.original.association.phenotype}
                      indentWidth={2}
                      displayDataTypes={false}
                      collapsed={true}
                      name={row.original.association.phenotype.description}
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
                accessor: "association.environmentalContexts.description",
                Filter: ({filter, onChange}) => (
                  <ColumnFilter  accessor={"association.environmentalContexts.description"}
                                 onChange={onChange} config={this.state.config} currentQuery={() => (this.state.current_query)} />
                ),
                Cell: (row) => {
                  const environmentalContexts = row.original.association.environmentalContexts;
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
                accessor: "association.evidence_label",
                Filter: ({filter, onChange}) => (
                  <ColumnFilter  accessor={"association.evidence_label"}
                                 onChange={onChange} config={this.state.config} currentQuery={() => (this.state.current_query)} />
                ),
                Cell: (row) => {
                  return <span>{row.original.association.evidence_label}</span>
                }
              },
              {
                Header: "description",
                accessor: "association.evidence.description",
                Filter: ({filter, onChange}) => (
                  <ColumnFilter  accessor={"association.evidence.description"}
                                 onChange={onChange} config={this.state.config} currentQuery={() => (this.state.current_query)} />
                ),
                Cell: (row) => {
                  if (row.original.association.evidence.length == 0) {
                    return <span/>
                  }
                  return <span>{row.original.association.evidence[0].description}</span>
                }
              },
              {
                Header: "publications",
                accessor: "association.evidence.info.publications",
                Filter: ({filter, onChange}) => (
                  <ColumnFilter  accessor={"association.evidence.info.publications"}
                                 onChange={onChange} config={this.state.config} currentQuery={() => (this.state.current_query)} />
                ),
                Cell: (row) => {
                  const evidence = row.original.association.evidence;
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
          console.log({ page: state.page, pageSize: state.pageSize, sorted: state.sorted, filtered: state.filtered, search_query: this.state.search_query, });
          // show the loading overlay
          if (!this.state.config) {
            return
          }
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
          var  q = this.state.search_query || '*'
          const filtered = state.filtered
            .map(f => {
              return f.id.replace('_source.','+') + ":\"" + f.value  +"\"";
              } )
            .join(' ')
          if (filtered.length > 0) {
            q = q + ' ' + filtered
          }

          // fetch your data
          if (this.state.config) {
            let _this = this;
            fetch(`${this.state.config.associations}?q=${q}&size=${state.pageSize}&from=${state.pageSize * state.page}&sort=${sorted}`)
              .then(function(response) {
                if (!response.ok) {
                    throw Error(response.statusText);
                }
                response.json().then(function(data) {
                          console.log('fetch data', data);
                          console.log('hits.length', data.hits.hits.length);
                          console.log('hits.total', data.hits.total);
                          _this.setState({
                            results: data.hits.hits,
                            pages: Math.ceil(data.hits.total / state.pageSize),
                            loading: false
                          });
                        })
                }
              ).catch(function(error) {
                // catch exceptions thrown above
                alert(error)
                console.trace(error);
              });
          }

          q = q || '*'
          this.setState({current_query: q})


          // client
          //   .search({
          //     q: q ,
          //     index: 'associations',
          //     from: state.pageSize * state.page,
          //     sort: sorted,
          //     size: state.pageSize
          //   })
          //   .then(
          //     function(body) {
          //       this.setState({
          //         results: body.hits.hits,
          //         pages: Math.ceil(body.hits.total / state.pageSize),
          //         loading: false
          //       });
          //     }.bind(this),
          //     function(error) {
          //       console.trace(error.message);
          //       this.setState({loading:false})
          //       alert(error.message);
          //     }.bind(this)
          //   );
        } //
      } // onFetchData
      />
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
          {this.renderTable()}
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
    const field = this.props.accessor // .replace('_source.','') + '.keyword';
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
    let _this = this;
    console.log(this)
    fetch(`${this.props.config.terms}?q=${q}&f=${field}`)
      .then(function(response) {
        response.json().then(function(data) {
                  console.log('terms data', data);
                  _this.setState({
                    dataSource: data.terms.buckets.map(b=>b.key)
                  });
                });
        }
      );


    // client
    //   .search({
    //     index: 'associations',
    //     body: {
    //         size: 0 ,
    //         query: {
    //           query_string: {
    //             query: q,
    //             analyze_wildcard: true
    //           }
    //         },
    //         aggs: {
    //           values: {
    //               terms: {
    //                   field: field,
    //                   size: 10,
    //                   order: {
    //                     _count: 'desc'
    //                   },
    //                   include:  value ? value + '.*' : value
    //               }
    //           }
    //         }
    //     }
    //   })
    //   .then(
    //     function(body) {
    //       //set choices
    //       this.setState({
    //         dataSource: body.aggregations.values.buckets.map(b=>b.key),
    //       });
    //     }.bind(this),
    //     function(error) {
    //       console.trace(error.message);
    //       alert(error.message);
    //     }.bind(this)
    //   );
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
