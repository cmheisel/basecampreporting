try:
    import xml.etree.cElementTree as ET
except ImportError:
    try:
        import xml.etree.ElementTree
    except ImportError:
        try:
            import cElementTree as ET
        except ImportError:
            from elementtree import ET
