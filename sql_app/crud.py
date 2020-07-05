from sqlalchemy.orm import Session

from sql_app import models, schemas


def create_blacklist(db: Session, blacklist: schemas.BlackListCreate):
    """
    插入黑名单网站
    :param db:
    :param blacklist: 黑名单对象
    :return: 插入成功的对象
    """
    domain = blacklist.domain
    db_blacklist = models.BlackDomain(domain=domain)
    db.add(db_blacklist)
    db.commit()
    db.refresh(db_blacklist)
    return db_blacklist


def get_blacklist(db: Session, domain: str):
    """
    检查数据库中是否存在某个黑名单域名
    :param db:
    :param domain: 域名
    :return: 查询结果
    """
    return db.query(models.BlackDomain).filter(models.BlackDomain.domain == domain).first()


def get_all_blacklist(db: Session):
    """
    获取所有黑名单域名
    :param db:
    :return: 所有黑名单域名
    """
    return db.query(models.BlackDomain).all()


def get_allow_domain(db: Session):
    """
    获取所有已经解析的域名
    :param db:
    :return:
    """
    return db.query(models.Rule.netloc).all()


def get_rule_by_netloc(db: Session, netloc: str):
    """
    根据域名获取相应规则
    :param db:
    :param netloc: 域名
    :return:
    """
    return db.query(models.Rule).filter(models.Rule.netloc == netloc).first()
