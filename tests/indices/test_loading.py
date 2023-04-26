from pathlib import Path
from typing import List
import pytest
from gpt_index.data_structs.node_v2 import Node
from gpt_index.indices.list.base import GPTListIndex
from gpt_index.indices.loading import load_index_from_storage, load_indices_from_storage
from gpt_index.indices.service_context import ServiceContext
from gpt_index.indices.vector_store.base import GPTVectorStoreIndex
from gpt_index.readers.schema.base import Document
from gpt_index.storage.storage_context import StorageContext


def test_load_index_from_storage_simple(
    documents: List[Document],
    tmp_path: Path,
    mock_service_context: ServiceContext,
):
    # construct simple (i.e. in memory) storage context
    storage_context = StorageContext.from_defaults(persist_dir=tmp_path)

    # construct index
    index = GPTVectorStoreIndex.from_documents(
        documents=documents,
        storage_context=storage_context,
        service_context=mock_service_context,
    )

    # persist storage to disk
    storage_context.persist()

    # load storage context
    new_storage_context = StorageContext.from_defaults(persist_dir=tmp_path)

    # load index
    new_index = load_index_from_storage(
        new_storage_context, service_context=mock_service_context
    )

    assert index.index_id == new_index.index_id


def test_load_index_from_storage_multiple(
    nodes: List[Node],
    tmp_path: Path,
    mock_service_context: ServiceContext,
):
    # construct simple (i.e. in memory) storage context
    storage_context = StorageContext.from_defaults(persist_dir=tmp_path)

    # construct multiple indices
    vector_index = GPTVectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        service_context=mock_service_context,
    )
    vector_id = vector_index.index_id

    list_index = GPTListIndex(
        nodes=nodes,
        storage_context=storage_context,
        service_context=mock_service_context,
    )

    list_id = list_index.index_id

    # persist storage to disk
    storage_context.persist()

    # load storage context
    new_storage_context = StorageContext.from_defaults(persist_dir=tmp_path)

    # load single index should fail since there are multiple indices in index store
    with pytest.raises(ValueError):
        load_index_from_storage(
            new_storage_context, service_context=mock_service_context
        )

    # test load all indices
    indices = load_indices_from_storage(storage_context)
    index_ids = [index.index_id for index in indices]
    assert len(index_ids) == 2
    assert vector_id in index_ids
    assert list_id in index_ids

    # test load multiple indices by ids
    indices = load_indices_from_storage(storage_context, index_ids=[list_id, vector_id])
    index_ids = [index.index_id for index in indices]
    assert len(index_ids) == 2
    assert vector_id in index_ids
    assert list_id in index_ids
