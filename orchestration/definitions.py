"""Dagster asset graph. Run from repository root: dagster dev -f orchestration/definitions.py"""
from dagster import asset, Definitions, MetadataValue
from orchestration.sources import load_sources
from orchestration.normalize import normalize, validate
from orchestration.pipeline import make_observability, save_csv, FIELDS, ROOT
import os

@asset(description='Official API optional; simulated feeds always clearly labeled')
def raw_public_documents():
    return load_sources(fetch_federal=os.environ.get('FETCH_FEDERAL_REGISTER','0')=='1')

@asset
def normalized_documents(raw_public_documents):
    return normalize(raw_public_documents)

@asset
def validated_documents(normalized_documents):
    return validate(normalized_documents)

@asset
def source_observability(context, validated_documents):
    r=make_observability(validated_documents,fetch_federal=os.environ.get('FETCH_FEDERAL_REGISTER','0')=='1')
    save_csv(ROOT/'artifacts/source_observability.csv',r,
             ['source_id','jurisdiction','kind','document_count','last_retrieved_at','status','coverage_note'])
    context.add_output_metadata({'sources':len(r),'sample_status':MetadataValue.text(r[0]['status'])})
    return r

@asset
def review_queue(context, validated_documents):
    save_csv(ROOT/'artifacts/normalized_documents.csv',validated_documents,FIELDS)
    save_csv(ROOT/'artifacts/public_review_queue.csv',validated_documents,FIELDS)
    context.add_output_metadata({'documents':len(validated_documents),'label':MetadataValue.text('SIMULATED unless sourced from public API')})
    return len(validated_documents)

defs=Definitions(assets=[raw_public_documents,normalized_documents,validated_documents,source_observability,review_queue])
