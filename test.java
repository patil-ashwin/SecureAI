[
  {
    "name": "load_job",
    "sys.data_root": "/tmp",
    "verbose": true,
    "dryrun": true,
    "interval": 1,
    "maxNumError": 1,
    "maxPercentError": 1,
    "dataSources": [
      {
        "filename": "f",
        "path": "./data",
        "name": "file"
      }
    ],
    "configs": {
      "CONCURRENCY": 2,
      "eof": "false",
      "BATCH_SIZE": 3
    }
  }
]
