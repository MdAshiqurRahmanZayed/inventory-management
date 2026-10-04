FROM odoo:19.0

USER root
COPY entrypoint.sh /custom-entrypoint.sh
RUN chmod +x /custom-entrypoint.sh
USER odoo

ENTRYPOINT ["/custom-entrypoint.sh"]
CMD ["odoo"]
