// -*- C++ -*-
//
// Package:     XMLTools
// Class  :     XMLDOMBlock
// 
// Implementation:
//     <Notes on implementation>
//
// Original Author:  Gena Kukartsev
//         Created:  Thu Sep 27 01:43:42 CEST 2007
// $Id: XMLDOMBlock.cc,v 1.2 2008/02/28 15:03:13 kukartse Exp $
//

// system include files
#include <string>
#include <xercesc/parsers/XercesDOMParser.hpp>
#include <xercesc/sax/HandlerBase.hpp>
#include <xercesc/dom/DOM.hpp>
#include<time.h>

#if defined(XERCES_NEW_IOSTREAMS)
#include <iostream>
#else
#include <iostream.h>
#endif

XERCES_CPP_NAMESPACE_USE 
using namespace std;

// user include files
#include "CaloOnlineTools/HcalOnlineDb/interface/XMLDOMBlock.h"
#include "CaloOnlineTools/HcalOnlineDb/interface/XMLProcessor.h"


//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
XMLDOMBlock::XMLDOMBlock()
{
  //cout << "XMLDOMBlock (or derived): default constructor called - this is meaningless!" << endl;
  //cout << "XMLDOMBlock (or derived): use yourClass( loaderBaseConfig & ) instead." << endl;
  init( "ROOT" );
}

XMLDOMBlock::XMLDOMBlock( string _root, int rootElementName )
{
  //cout << "XMLDOMBlock (or derived): default constructor called - this is meaningless!" << endl;
  //cout << "XMLDOMBlock (or derived): use yourClass( loaderBaseConfig & ) instead." << endl;
  init( _root );
}


XMLDOMBlock::XMLDOMBlock( InputSource & _source )
{

  theProcessor = XMLProcessor::getInstance();

  //theFileName = xmlFileName;

  // initialize the parser
  parser = new XercesDOMParser();
  parser->setValidationScheme(XercesDOMParser::Val_Always);    
  parser->setDoNamespaces(true);    // optional
  
  errHandler = (ErrorHandler*) new HandlerBase();
  parser->setErrorHandler(errHandler);

  // parse the input xml file
  try
    {
      parser->parse( _source );
    }
  catch (const XMLException& toCatch) {
    char* message = XMLString::transcode(toCatch.getMessage());
    cout << "Exception message is: \n"
	 << message << "\n";
    XMLString::release(&message);
    //return -1;
  }
  catch (const DOMException& toCatch) {
    char* message = XMLString::transcode(toCatch.msg);
    cout << "Exception message is: \n"
	 << message << "\n";
    XMLString::release(&message);
    //return -1;
  }
  catch (...) {
    cout << "Unexpected Exception \n" ;
    //return -1;
  }

  //get the XML document
  document = parser -> getDocument();
}



int XMLDOMBlock::init( string _root )
{
  theProcessor = XMLProcessor::getInstance();

  //theFileName = xmlFileName;

  // initialize the parser
  parser = new XercesDOMParser();
  parser->setValidationScheme(XercesDOMParser::Val_Always);    
  parser->setDoNamespaces(true);    // optional
  
  errHandler = (ErrorHandler*) new HandlerBase();
  parser->setErrorHandler(errHandler);

  DOMImplementation* impl =  DOMImplementation::getImplementation();
  
  document = impl->createDocument(
				  0,                      // root element namespace URI.
				  //XMLString::transcode("ROOT"), // root element name
				  XMLProcessor::_toXMLCh(_root), // root element name
				  0);                     // document type object (DTD).

  the_string = NULL;

  return 0;
}



XMLDOMBlock::XMLDOMBlock( string xmlFileName )
{

  theProcessor = XMLProcessor::getInstance();

  theFileName = xmlFileName;

  // initialize the parser
  parser = new XercesDOMParser();
  parser->setValidationScheme(XercesDOMParser::Val_Always);    
  parser->setDoNamespaces(true);    // optional
  
  errHandler = (ErrorHandler*) new HandlerBase();
  parser->setErrorHandler(errHandler);

  // parse the input xml file
  try
    {
      parser->parse( theFileName . c_str() );
    }
  catch (const XMLException& toCatch) {
    char* message = XMLString::transcode(toCatch.getMessage());
    cout << "Exception message is: \n"
	 << message << "\n";
    XMLString::release(&message);
    //return -1;
  }
  catch (const DOMException& toCatch) {
    char* message = XMLString::transcode(toCatch.msg);
    cout << "Exception message is: \n"
	 << message << "\n";
    XMLString::release(&message);
    //return -1;
  }
  catch (...) {
    cout << "Unexpected Exception \n" ;
    //return -1;
  }

  //get the XML document
  document = parser -> getDocument();

}

DOMDocument * XMLDOMBlock::getNewDocument( string xmlFileName )
{
  delete document;

  theProcessor = XMLProcessor::getInstance();

  theFileName = xmlFileName;

  // initialize the parser
  parser = new XercesDOMParser();
  parser->setValidationScheme(XercesDOMParser::Val_Always);    
  parser->setDoNamespaces(true);    // optional
  
  errHandler = (ErrorHandler*) new HandlerBase();
  parser->setErrorHandler(errHandler);

  // parse the input xml file
  try
    {
      parser->parse( theFileName . c_str() );
    }
  catch (const XMLException& toCatch) {
    char* message = XMLString::transcode(toCatch.getMessage());
    cout << "Exception message is: \n"
	 << message << "\n";
    XMLString::release(&message);
    //return -1;
  }
  catch (const DOMException& toCatch) {
    char* message = XMLString::transcode(toCatch.msg);
    cout << "Exception message is: \n"
	 << message << "\n";
    XMLString::release(&message);
    //return -1;
  }
  catch (...) {
    cout << "Unexpected Exception \n" ;
    //return -1;
  }

  //get the XML document
  document = parser -> getDocument();

  return document;
}

DOMDocument * XMLDOMBlock::getDocument( void )
{
  return document;
}

int XMLDOMBlock::write( string target )
{
  theProcessor -> write( this, target );

  return 0;
}

XMLDOMBlock::~XMLDOMBlock()
{
  delete parser;
  delete errHandler;
  if (the_string) delete the_string;
}

const char * XMLDOMBlock::getTagValue( const string & tagName, int _item, DOMDocument * _document )
{
  if (!_document) _document = document;
  const char * _result = XMLString::transcode( _document -> getElementsByTagName( XMLProcessor::_toXMLCh( tagName ) ) -> item( _item ) -> getFirstChild()-> getNodeValue() );
  return _result;
}

int XMLDOMBlock::setTagValue( const string & tagName, const string & tagValue, int _item, DOMDocument * _document )
{
  if (!_document) _document = document;
  _document -> getElementsByTagName( XMLProcessor::_toXMLCh( tagName ) ) -> item( _item ) -> getFirstChild() -> setNodeValue( XMLProcessor::_toXMLCh( tagValue ) );
  return 0;
}

int XMLDOMBlock::setTagValue( const string & tagName, const int & tagValue, int _item, DOMDocument * _document )
{
  if (!_document) _document = document;
  _document -> getElementsByTagName( XMLProcessor::_toXMLCh( tagName ) ) -> item( _item ) -> getFirstChild() -> setNodeValue( XMLProcessor::_toXMLCh( tagValue ) );
  return 0;
}

const char * XMLDOMBlock::getTagAttribute( const string & tagName, const string & attrName, int _item )
{
  DOMElement * _tag = (DOMElement *)(document -> getElementsByTagName( XMLProcessor::_toXMLCh( tagName ) ) -> item( _item ));
  const char * _result = XMLString::transcode( _tag -> getAttribute( XMLProcessor::_toXMLCh( attrName ) ) );

  return _result;
}

int XMLDOMBlock::setTagAttribute( const string & tagName, const string & attrName, const string & attrValue, int _item )
{
  DOMElement * _tag = (DOMElement *)(document -> getElementsByTagName( XMLProcessor::_toXMLCh( tagName ) ) -> item( _item ));
  _tag -> setAttribute( XMLProcessor::_toXMLCh( attrName ), XMLProcessor::_toXMLCh( attrValue ) );

  return 0;
}

string XMLDOMBlock::getTimestamp( time_t _time )
{
  char timebuf[50];
  //strftime( timebuf, 50, "%c", gmtime( &_time ) );
  strftime( timebuf, 50, "%Y-%m-%d %H:%M:%S.0", gmtime( &_time ) );
  string creationstamp = timebuf;

  return creationstamp;
}




std::string & XMLDOMBlock::getString( void )
{
  return getString( this->getDocument() );
}




std::string & XMLDOMBlock::getString( DOMNode * _node )
{
  if (the_string) delete the_string;
  std::string _target = "string";
  the_string = new std::string( XMLString::transcode( theProcessor->serializeDOM(_node,_target) ) );
  return (*the_string);
}



