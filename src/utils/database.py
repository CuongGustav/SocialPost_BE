from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tạo engine để kết nối với PostgreSQL
engine = create_engine(DATABASE_URL, echo=True)

# Tạo session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Cung cấp một session database và đảm bảo quản lý giao dịch đúng cách.
    """
    db = SessionLocal()
    logger.info("Opening database session")
    try:
        yield db
        db.commit()  # Commit giao dịch nếu không có lỗi
        logger.info("Committing database session")
    except Exception as e:
        logger.error(f"Error in database session: {str(e)}")
        db.rollback()  # Rollback nếu có lỗi
        logger.info("Rolling back database session")
        raise
    finally:
        db.close()
        logger.info("Closing database session")